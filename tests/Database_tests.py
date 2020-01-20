from __future__ import print_function
import database_stuff
import image_corruption_utils

###
# These tests require two jpg files, one named "test1.jph" and the other named "test2.jpg".
###

if __name__ == "__main__":
    ###
    # Currently testing the ability to add hashes and connect. The isCorrupt field is deliberately set as well and is
    # not authentic to the image at hand (for this test it doesn't matter).
    ###
    database_stuff.store_image("test1.jpg", False, image_corruption_utils.getLocalHash("test1.jpg"), 7)
    database_stuff.store_image("test1.jpg", True, image_corruption_utils.getLocalHash("test2.jpg"))
    #database_stuff.update_entry("test1.jpg", True, datetime.now(timezone.utc).date().strftime('%B/%d/%Y'), image_corruption_utils.getLocalHash("test.jpg"))