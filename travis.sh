#/usr/bin/env bash
git clone https://github.com/CuriouslyCurious/dotfiles.git $HOME/dotfiles

echo "=========================="
echo "First run"
echo "=========================="
yes | python3 stow.py 
ls -la $HOME/.config

echo "=========================="
echo "Ensure it doesn't stow when something exists."
echo "=========================="
yes | python3 stow.py 
ls -la $HOME/.config

echo "=========================="
echo "Check if replacing stuff works"
echo "=========================="
yes | python3 stow.py -R
ls -la $HOME/.config

echo "=========================="
echo "Remove everything"
echo "=========================="
yes | python3 stow.py -r
ls -la $HOME/.config

echo "=========================="
echo "Try to run again and see if anything remained"
echo "=========================="
yes | python3 stow.py
ls -la $HOME/.config

echo "=========================="
echo "Remove everything again."
echo "=========================="
yes | python3 stow.py
ls -la $HOME
ls -la $HOME/.config
