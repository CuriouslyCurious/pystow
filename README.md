# pystow
[![Github file size](https://img.shields.io/github/size/webcaetano/craft/build/phaser-craft.min.js.svg)]() [![license](https://img.shields.io/github/license/mashape/apistatus.svg)]()

A replacement for `stow` written in python 3.

It was made out of my own frustrations with how clunky and un-moving the original `stow` was. It was very tedious to have to stow each individual folder to get all the config files up and running. And, you couldn't stow if there was any kind of conflict or if it was outside of your home folder. Then there was the problem of having to install an extra program when you don't always have root access just to manage your dotfiles.

I also tried `stowsh` which was good for portability as it is written in `bash`, but it's implementation left something to be desired. 

So, I made my own *fancier* version. ;)

## Warning
This script can be a bit dangerous and may break configuration files / folders. Please back-up your existing configurations if you fear for their puny lives.

I will not take any responsibility for anyone who accidentally deletes their entire configuration library. Use this script at your own risk!

## Requirements
`Python 3.4` or above.

No external dependencies. :D

## License
See [LICENSE.md](LICENSE.md).

