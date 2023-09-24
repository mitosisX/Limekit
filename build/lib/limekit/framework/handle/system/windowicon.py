from PySide6.QtGui import QIcon, QImage
import os

class WindowIcon:
    """
    ** Platform-dependently determines the right window icon to be used.
    
    - But, I think it would be best not to let the user specify the window
      icons directly but rather have them rename the icons with (icon-size.png)
      like, app-16, app-32 and app-48 PNG's and only type the app.png
      and not the whole name explicitly, the rest should be determined by
      the engine.
        
    
    window_icon = Window()
    window.setIcon(images('app.png')) 
    
    * Here, the system shall find the right icon size automtically
    """
    def choose_icon(icon_filenames):
        system_icon_size = QIcon.fromTheme("application-icon").availableSizes()[0]
        sizes = []
        
        for filename in icon_filenames:
            if os.path.isfile(filename):
                image = QImage(filename)
                sizes.append(image.width())
        sizes = sorted(set(sizes), reverse=True)
        
        for size in sizes:
            if size >= system_icon_size:
                icon_filename = next((filename for filename in icon_filenames if str(size) in filename), None)
                if icon_filename:
                    return QIcon(icon_filename)
        return None