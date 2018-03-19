#/usr/bin/env bash
git clone https://github.com/CuriouslyCurious/dotfiles.git $HOME/dotfiles
stow.py
yes | python3 stow.py 
yes | python3 stow.py 
yes | python3 stow.py -R
yes | python3 stow.py -r
yes n | python3 stow.py
