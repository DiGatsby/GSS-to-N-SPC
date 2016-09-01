# GSS-to-N-SPC
Small converter to convert SNES GSS tracker's SPC format to N-SPC format. 

##Doesn't work with vanilla SNES GSS!
I build modified version of SNES GSS to be used with this converter. Only differences being that it doesn't use long delays and doesn't add very small delays after every note. (Which in original is used to prevent clicking)

I'll try to make my SNES GSS fork available when I can. In the meantime you can try to build it yourself (Requires Borland C++ compiler) and modify it to not use the long delay command. Removing the small delays that prevent clicking is optional. (Leaving them in makes the song quite large though)
