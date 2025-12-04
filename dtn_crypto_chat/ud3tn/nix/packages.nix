# SPDX-License-Identifier: BSD-3-Clause OR Apache-2.0

{ pkgs, ... }:

let
  version = "0.14.2";
in

rec {
  ud3tn = pkgs.stdenv.mkDerivation {
    pname = "ud3tn";
    inherit version;

    src = pkgs.lib.sourceByRegex ../. [
      "Makefile"
      "^components.*"
      "^external.*"
      "^generated.*"
      "^include.*"
      "^mk.*"
    ];

    buildInputs = [
      pkgs.sqlite
    ];

    buildPhase = ''
      make type=release optimize=yes -j $NIX_BUILD_CORES ud3tn
    '';

    installPhase = ''
      mkdir -p $out/bin
      cp build/posix/ud3tn $out/bin/
    '';
  };

  pyd3tn = with pkgs.python3Packages; buildPythonPackage {
    pname = "pyd3tn";
    inherit version;
    src = ../pyd3tn;
    format = "pyproject";
    nativeBuildInputs = [ setuptools ];
    propagatedBuildInputs = [ cbor2 ];
  };

  python-ud3tn-utils = with pkgs.python3Packages; buildPythonPackage {
    pname = "python-ud3tn-utils";
    inherit version;
    src = ../python-ud3tn-utils;
    format = "pyproject";
    nativeBuildInputs = [ setuptools ];
    propagatedBuildInputs = [ cbor2 protobuf pyd3tn ];
  };

  mkdocs-html = pkgs.stdenv.mkDerivation {
    pname = "mkdocs-html";
    inherit version;

    src = pkgs.lib.sourceByRegex ../. [
      "^doc.*$"
      "^include.*"
      "^components.*"
      "^pyd3tn.*"
      "^python-ud3tn-utils.*"
      "mkdocs.yaml"
    ];

    nativeBuildInputs = with pkgs; [
      doxygen
    ] ++ (with python3Packages; [
      mkdocs
      mkdocs-material
      mkdocstrings
      mkdocstrings-python
      (
        buildPythonPackage rec {
          pname = "mkdoxy";
          version = "1.2.4";
          src = fetchPypi {
            inherit pname version;
            sha256 = "14a2bd1df990f34f81d180d2dec62c29e387ec2f2984032374855c37bc5b020b";
          };
          doCheck = false;
        }
      )
    ]);

    buildPhase = ''
      mkdocs build --site-dir $out
    '';
  };
}
