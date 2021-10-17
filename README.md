# Readme  
  
This is a small program I threw together in about 6 hours to block out your face. It probably doesn't work very well, so be warned.  
By default, the program will use a green rectangle to block out your face and show the result in a window. The 'b' key can be used to toggle the blocking functionality in case you want to do that for some reason.  
  
## Syntax
```
py -3 src/main.py [options]

-h, --help             Display the help menu
-v, --verbose          Run the program in verbose mode
-i, --image [path]     Block out faces with an image instead of a green rectangle
-w, --hide-window      Run the program without display output to a window
-c, --camera           Outputs the program to a virtual camera
```

## Deps
- opencv2
- numpy (Only required if you want to use the -i and -c flags)
- pyvirtualcam  (Only required if you want to use the -c flag)