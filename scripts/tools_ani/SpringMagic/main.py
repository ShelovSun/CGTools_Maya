import SpringMagic
import SpringMagic.ui as ui

def main(*args, **kwargs):

    widget = ui.SpringMagicWidget()
    widget.show()


if __name__ == "__main__":

    with SpringMagic.app():
        SpringMagic.main()
