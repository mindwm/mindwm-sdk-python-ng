{
  description = "A MindWM SDK for Python";

  inputs = {
    #nixpkgs.url = "github:nixos/nixpkgs/24.05";
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    parliament-py.url = "github:omgbebebe/parliament.py-nix";
    parliament-py.inputs.nixpkgs.follows = "nixpkgs";
    neontology-py.url = "github:omgbebebe/neontology.py-nix";
    neontology-py.inputs.nixpkgs.follows = "nixpkgs";
    devshell.url = "github:numtide/devshell/main";
    devshell.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs@{ flake-parts, nixpkgs, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.devshell.flakeModule
      ];
      systems = [ "x86_64-linux" "aarch64-linux" ];
      perSystem = { config, self', inputs', pkgs, system, ... }:
      let
        my_python = pkgs.python3.withPackages (ps: with ps; [
          inputs.parliament-py.packages.${system}.default
          inputs.neontology-py.packages.${system}.default
          pydantic dateutil urllib3
          opentelemetry-sdk opentelemetry-exporter-otlp
          neo4j
          pandas
        ]);
        project = pkgs.callPackage ./package.nix {
          my_python = my_python;
        };
      in { 
        packages.default = project;
        devshells.default = {
            env = [];
            devshell.startup.pypath = pkgs.lib.noDepEntry ''
              export PYTHONPATH="$PYTHONPATH:./src"
            '';
            commands = [ ];
            packages = [
              my_python
            ] ++ (with pkgs; [
            ]);
        };
      };
      flake = {
      };
    };
}
