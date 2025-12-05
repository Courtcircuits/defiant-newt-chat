
import sys
import os
import asyncio
import cbor2
import json
from utils import (
        encrypt_message,
        decrypt_message,
        get_current_date,
        compute_hash_chain,
        set_fake_date
)

from ud3tn_utils.aap2 import (
        AAP2TCPClient,
        AAP2UnixClient,
        AuthType,
        BundleADU,
        BundleADUFlags,
        ResponseStatus,
)

from pyd3tn.bundle7 import (
    BibeProtocolDataUnit,
    Bundle,
    PayloadBlock,
    PrimaryBlock,
)

import datetime



not_the_flag = "N3WT{d3tn_crypt0_ch4t_ftw_but_n3xt_1s_b4d}"


user_name = sys.argv[1]
user_socket = sys.argv[2]
newest_revocation_status = sys.argv[3] # in hex() format
secret = sys.argv[4]
destination_name = sys.argv[5]
key = bytes.fromhex(sys.argv[6])
destination_cert_issuance_date = sys.argv[7] # in date().isoformat()
destination_validity_hash = sys.argv[8] # in hex() format
manipulated_date_str = sys.argv[9]
pipe_name = sys.argv[10]
port = int(sys.argv[11])
agentid = f"{user_name.replace(' ', '').lower()}{destination_name.replace(' ', '').lower()}"

if manipulated_date_str:
    manipulated_date = datetime.datetime.fromisoformat(manipulated_date_str)
    set_fake_date(manipulated_date)
print("The current date is: ", get_current_date().date())
print("Starting bot")


async def recv_aap2(aap2_client, max_count, verify_pl, newline, user_name, destination_name, key, destination_cert_issuance_date, destination_validity_hash, bot):
    counter = 0
    loop = asyncio.get_event_loop()
    while True:
        # Run the blocking receive_msg() in a thread pool to avoid blocking the event loop
        msg = await loop.run_in_executor(None, aap2_client.receive_msg)
        if not msg:
            print("No message received. Exiting receive loop.")
            return
        msg_type = msg.WhichOneof("msg")
        if msg_type == "keepalive":
            print("Received keepalive message, acknowledging.")
            aap2_client.send_response_status(
                ResponseStatus.RESPONSE_STATUS_ACK
            )
            continue
        elif msg_type != "adu":
            print("Received message with field '%s' set, discarding.", msg_type)
            continue
        adu_msg, bundle_data = aap2_client.receive_adu(msg.adu)
        aap2_client.send_response_status(
            ResponseStatus.RESPONSE_STATUS_SUCCESS
        )

        enc = False
        err = False

        if BundleADUFlags.BUNDLE_ADU_BPDU in adu_msg.adu_flags:
            payload = cbor2.loads(bundle_data)
            bundle = Bundle.parse(payload[2])
            payload = bundle.payload_block.data
            enc = True
        else:
            payload = bundle_data
        
        if not err:
            enc = " encapsulated" if enc else ""
            print(
                "Received%s bundle from '%s', payload len = %d",
                enc,
                msg.adu.src_eid,
                len(payload),
            )

            if verify_pl is not None and verify_pl.encode("utf-8") != payload:
                print("Unexpected payload != '%s'", verify_pl)
                sys.exit(1)

            try:
                message = json.loads(payload)
                print("Received message: %s", message)

                days_passed = (get_current_date().date() - datetime.datetime.fromisoformat(destination_cert_issuance_date).date()).days
                try:
                    assert bytes.fromhex(destination_validity_hash) == compute_hash_chain(bytes.fromhex(message.get("status")), days_passed) or bytes.fromhex(destination_validity_hash) == compute_hash_chain(bytes.fromhex(message.get("status")), days_passed + 1) or bytes.fromhex(destination_validity_hash) == compute_hash_chain(bytes.fromhex(message.get("status")), days_passed - 1)

                except AssertionError:
                    print("ERROR: Invalid hash value - must have been modified!")
                    raise
                line_to_write = f"{destination_name}: {decrypt_message(key, message.get('message'))}"
                if len(line_to_write) < len(user_name) + 2:
                    line_to_write += " " * (len(user_name) + 2 - len(line_to_write))
                await bot.run_bot()
            except json.JSONDecodeError as e:
                print("Failed to decode message payload: %s", e)
        else:
            print("Received administrative record of unknown type from '%s'!",
            msg.adu.src_eid)
        counter += 1
        if max_count and counter >= max_count:
            print("Expected amount of bundles received, terminating.")
            return


def send_message(
        payload, dest_eid, agentid, socket,
        secret,
        tcp=None,
        verbosity=0,
        bdm_auth=False,
        ):
    if payload is not None:
        payload = payload.encode("utf-8")
    else:
        raise ValueError("Payload must be provided!")

    if tcp:
        aap2_client = AAP2TCPClient(address=tcp)
    else:
        aap2_client = AAP2UnixClient(address=socket)
    with aap2_client:
        aap2_client.configure(
            agentid,
            subscribe=False,
            secret=secret,
            auth_type=(
                AuthType.AUTH_TYPE_DEFAULT if not bdm_auth
                else AuthType.AUTH_TYPE_BUNDLE_DISPATCH
            ),
        )
        flags = [BundleADUFlags.BUNDLE_ADU_NORMAL]
        if bdm_auth:
            flags += [BundleADUFlags.BUNDLE_ADU_WITH_BDM_AUTH]
        aap2_client.send_adu(
            BundleADU(
                dst_eid=dest_eid,
                payload_length=len(payload),
                adu_flags=flags,
            ),
            payload,
        )
        assert (
                aap2_client.receive_response().response_status ==
                ResponseStatus.RESPONSE_STATUS_SUCCESS
        )

class BNPBot:
    def __init__(
            self,
            agentid,
            user_name,
            user_socket,
            secret,
            destination_name,
            key,
            destination_cert_issuance_date,
            destination_validity_hash,
            tcp=None,
            verbosity=0,
            count=None,
            verify_pl=None,
            newline=True,
            keepalive_seconds=None
            ):
        self.agentid = agentid
        self.user_name = user_name
        self.user_socket = user_socket
        self.secret = secret
        self.destination_name = destination_name
        self.key = key
        self.destination_eid = f"dtn://{self.destination_name.replace(' ', '-').lower()}.dtn/"
        self.destination_agentid = f"{self.destination_name.replace(' ', '').lower()}{self.user_name.replace(' ', '').lower()}"
        self.destination_cert_issuance_date = destination_cert_issuance_date
        self.destination_validity_hash = destination_validity_hash
        self.tcp = tcp
        self.verbosity = verbosity
        self.count = count
        self.verify_pl = verify_pl
        self.newline = newline
        self.keepalive_seconds = keepalive_seconds


    async def listen(self ):
        print("Starting to listen for incoming messages")
        try:
            if self.tcp:
                aap2_client = AAP2TCPClient(address=self.tcp)
            else:
                aap2_client = AAP2UnixClient(address=self.user_socket)
            with aap2_client:
                secret_value = aap2_client.configure(
                    self.agentid,
                    subscribe=True,
                    secret=self.secret,
                    keepalive_seconds=self.keepalive_seconds,
                )
                # this is now async
                await recv_aap2(
                        aap2_client,
                        self.count,
                        self.verify_pl,
                        self.newline,
                        self.user_name,
                        self.destination_name,
                        self.key,
                        self.destination_cert_issuance_date,
                        self.destination_validity_hash,
                        self
                )
        finally:
            print("Closing output stream")

    async def run_bot(self):
        # Sorry team but I was to tired to try to hide the flag more than that :( but pls give the money we 
        # implemented an exploit for the CVE 10/10 of next + we implemented a websocket client for an 
        # inter-planetary protocol !!!
        encrypted_flag = encrypt_message(key, not_the_flag)
         # ooooops I did it again :(
        encrypted_flag = encrypt_message(key, encrypted_flag)
        payload = {
                "message": encrypted_flag,
                "status": newest_revocation_status
        }
        payload_str = json.dumps(payload)
        send_message(
                payload=payload_str,
                dest_eid=self.destination_eid + self.destination_agentid,
                agentid=self.agentid,
                socket=self.user_socket,
                secret=self.secret
        )

service_instance = BNPBot(
        agentid,
        user_name,
        user_socket,
        secret,
        destination_name,
        key,
        destination_cert_issuance_date,
        destination_validity_hash,
        tcp=None,
        verbosity=0,
        count=None,
        verify_pl=None,
        newline=True,
        keepalive_seconds=None
)

async def main():
    await service_instance.listen()

if __name__ == "__main__":
    asyncio.run(main())
