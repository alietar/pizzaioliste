{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    nativeBuildInputs = with pkgs.buildPackages; [ python3 python310Packages.aiohttp python310Packages.aiosqlite chromium python310Packages.discordpy ];
}
