# pystow
[![Github file size](https://img.shields.io/github/size/webcaetano/craft/build/phaser-craft.min.js.svg)]() [![license](https://img.shields.io/github/license/mashape/apistatus.svg)]()

A replacement for [`stow`](https://www.gnu.org/software/stow/) written in python 3.

This program was made due to my frustrations with how clunky and un-moving the original `stow` was. I do like stow, but it is not very useful in managing larger dotfile collections. It is very tedious to have to stow each individual folder to get all the config files up and running. And, if you even thought about stow-ing when there was any kind of conflict you'd be given an error message and had to manually fix the problem. There's also the little problem of having to install a separate program to begin with; you don't always have root access.

I also tried [`stowsh`](https://github.com/williamsmj/stowsh) which was good for portability as it is written in `bash`, but it's implementation left something to be desired.

So, I decided I should make my own *fancier* version. ;)

## Requirements
`Python 3.4` or above.

No external dependencies. :D

## Installation

### Download
**curl**
```sh
curl https://raw.githubusercontent.com/CuriouslyCurious/pystow/master/stow.py --output stow.py
```

**wget**
```sh
wget https://raw.githubusercontent.com/CuriouslyCurious/pystow/master/stow.py
```

### Optional step
Add the script to your `$PATH` if you want to be able to run it from anywhere:
```sh
# make stow.py executable
chmod +x stow.py
# move stow.py to a $PATH folder
sudo mv stow.py /usr/bin/stow.py
```

## Warning
This script can be a bit dangerous and may break configuration files / folders. Please back-up your existing configurations if you fear for their puny lives.

I will not take any responsibility for anyone who accidentally deletes their entire configuration library. Use this script at your own risk!

## Alternatives
* https://www.gnu.org/software/stow/ - the original stow
* https://github.com/williamsmj/stowsh - a version of stow written in bash

## License
See [LICENSE.md](LICENSE.md).

