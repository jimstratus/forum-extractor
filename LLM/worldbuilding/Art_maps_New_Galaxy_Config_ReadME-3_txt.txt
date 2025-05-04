Modified Galaxy Configuration for Star Wars:Rebellion computer game

by DarthTex 2008-04-16
*** UPDATED 2009-05-12 by DarthTex ***
*** UPDATED 2011-08-24 by DarthTex ***

Use at your own risk.  I'm not responsible for any problems associated with this mod (If you can follow directions everything should work fine).  If you run into a problem, reload your original files from the CD or backups & try again.  Still have problems, or just have some questions, contact me at www.swrebellion.com (you'll have to register to send me a message.  I would give out my e-mail, but I don't want to be spammed for years on end if this file gets around in the future. lol).


This is the "Read me" file for modifying the original ingame galaxy for a configuration more approximate to the canon galaxy layout for the Star Wars galaxy we've seen in the movies and read about in the books.  Due to game restrictions, the exact configuration of sectors and systems within is mostly "symbolic" as the game has one sector size.  Also, the majority of systems have been changed to match the now used sectors.  

Attached are several files that can directly replace the original files.  I would suggest making backup copies of all files before replacing them with the modified versions.  WARNING!  Any changes you have made to these files for other mods or for your own use, will be lost when using these modified versions!!  As the STRATEGY.DLL is prohibitively large to include, I've provided instructions and the necessary files for you, the user, to modify it yourself; you'll need a copy of the program "ResourceHacker" to pull this off (http://www.angusj.com/resourcehacker/).  

Files included and their function:

1) Modified Galaxy SECTORSD.DAT : Contains the new sector name locations, game importance and game size configurations.
2) Modified Galaxy SYSTEMSD.DAT : Contains the new system locations, corresponding sector and system icon data.
3) Modified Galaxy TEXTSTRA.DLL : Contains the new sector and systems names.
4) Modified Galaxy ENCYTEXT.DLL : Contains the new encyclopedia data on each system.
5) Modified Galaxy Asteroid Field EDATA.177 : New encyclopedia graphic for asteroid fields.
6) Modified Galaxy Opening Galaxy.BMP : The new galaxy picture seen at the beginning of the game.
7) Modified Galaxy Ingame Galaxy.BMP : The new galaxy picture seen during the game.
8) Modified Galaxy Asteroid Icon.BMP : System icon for asteroid fields.

I would suggest creating a sub-folder for the game called "New Galaxy Config" and putting all the files therein.  The first five files can directly replace files in the game directories (don't forget to make your backup copies!  Only the CAPITAL letter words are needed; i.e. "Modified Galaxy SECTORSD.DAT" = "SECTORSD.DAT").  Files 1 & 2 are located in the GDATA directory, files 3 & 4 are located in the program directory (where REBEXE.EXE is located), and file 5 is located in the EDATA directory.  Files 6 thru 8 are used in the STRATEGY.DLL file (which is located in the program directory).


Modifying STRATEGY.DLL

Using ResourceHacker, open the STRATEGY.DLL file.
Click on the "+" next to the BITMAP folder to display the sub-folders within.

Click on the "+" next to sub-folder 902.
Click on the data label "1033" (you should see the picture of the opening galaxy used in the game).
Right-click on the data label "1033" and a sub-menu appears.  Click on "Replace Resource".
Click on "Open file with new bitmap" (top left hand corner; a directory will appear).  Browse to the file "Modified Galaxy Opening Galaxy.BMP" and click on "Open".
Click on "Replace" to load the new opening galaxy file.

Click on the "+" next to sub-folder 903.
Click on the data label "1033" (you should see the picture of the galaxy seen during the game).
Right-click on the data label "1033" and a sub-menu appears.  Click on "Replace Resource".
Click on "Open file with new bitmap" (a directory will appear).  Browse to the file "Modified Galaxy Ingame Galaxy.BMP" and click on "Open".
Click on "Replace" to load the new ingame galaxy file.

*** START OF UPDATE 1 ***
*
*  OLD => Scan down to the sub-folder 10223 and click on the "+" next to sub-folder.
*  OLD => Click on the data label "1033" (you should see the system icon of a planet).
*  OLD => Right-click on the data label "1033" and a sub-menu appears.  Click on "Replace Resource".
*  OLD => Click on "Open file with new bitmap" (a directory will appear).  Browse to the file "Modified Galaxy Asteroid Icon.BMP" and click on "Open".
*  OLD => Click on "Replace" to load the new system icon of an asteroid field.
*
*  If the "Asteroid Icon" is "messed up" during the game, use the following steps to fix the problem.  
*  Use this step in place of the previous OLD step to insert the asteroid field system icon.
*
*  Scan down to the sub-folder 10240 and click on the "+" next to sub-folder.
*  Click on the data label "1033" (you should see the system icon of a planet or an asteroid field).
*  Right-click on the data label "1033" and a sub-menu appears.  Click on "Save [Bitmap : 10240 : 1033]".
*  Type in the save file name "TempAstrd", and remember which directory the file is saved.
*
*  Scan up to the sub-folder 10223 and click on the "+" next to sub-folder.
*  Click on the data label "1033" (you should see the system icon of a planet or an asteroid field).
*  Right-click on the data label "1033" and a sub-menu appears.  Click on "Replace Resource".
*  Click on "Open file with new bitmap" (a directory will appear).  Browse to the file "TempAstrd" and click on "Open".
*  Click on "Replace" to load the new system icon of an asteroid field.
*
*** END OF UPDATE 1 ***

*** START OF UPDATE 2 ***
*
*  The Modified Galaxy ENCYTEXT.DLL file has been updated for the systems "Codia" and "Xal".
*  The system descriptions in the ENCYTEXT.DLL wouldn't update, but has now been fixed.
*
*** END OF UPDATE 2 ***

Click on "File" in the window menu and "Save" the file.  That's all there is to it.

Now when Rebellion starts up, you'll seen a new galaxy in the opening scene, a new layout during gameplay with sectors and systems laid out in a more "Star Wars" fashion.  Just remember, this is only a cosmetic change, and the game plays exactly the same.  Have fun and enjoy!

