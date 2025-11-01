{
  description = "Develop Python on Nix with uv";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.python3
              pkgs.uv
            ];

            shellHook = ''
              # Ensure uv uses Nix's python, not a downloaded one
              unset PYTHONPATH
              export UV_PYTHON="${pkgs.python3}/bin/python3"

              # Create the venv if missing, using the Nix Python
              if [ ! -d ".venv" ]; then
                uv venv --python "$UV_PYTHON" .venv
              fi

              # Sync deps without downloading a foreign Python
              uv sync --no-python-downloads

              # Activate the venv (now guaranteed to exist)
              . .venv/bin/activate

              echo "Using Python: $(command -v python3)"
              python3 -V
            '';
          };
        }
      );
    };
}
