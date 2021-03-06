# -*- coding: UTF-8 -*-
# Purpose of this file is to follow up with any tagged images
# tagged images are tagged with a template that adds them to a category.
# The template that adds the images to the category has an unnamed parameter
# for the date that the tag was added. This tag is to be scanned in order to
# determine whether the file should now be nominated for deletion.

# Nominating for deletion occurs after 30 days have passed. The image should
# also be re-checked prior to nomination to ensure that it has not been fixed.
# If the image is fixed, then remove the template and take no further action.

# This should _really_ be done using a database. Perhaps pybind11 eventually(?)

from __future__ import absolute_import

import mwparserfromhell, os
from image_corruption_utils import *
from PIL import UnidentifiedImageError
from database_stuff import get_expired_images, calculate_difference, update_entry
import pywikibot
import pwb_wrappers
from image_corruption_utils import notify_user


def notify_and_tag(site, filepage, days):
    pwb_wrappers.tag_page(filepage, "{{SD|Corrupt image that has not been resolved in " + str(days) + "}}",
                          "Nominating corrupt file for deletion - passed " + str(days) + " day grace period.",
                          minor=False)
    notify_user(site, filepage, days, 'followup', day_count=days)


def run(site, image, isCorrupt, date_scanned, to_delete_nom):
    image_page = pywikibot.Page(site, image)  # does this need to be FilePage?

    if not allow_bots(image_page.text, "TheSandBot"):
        print("Not to edit " + image_page.title())
        return

    text = failed = img_hash = None
    _, ext = os.path.splitext(image_page.title())  # get filetype
    download_attempts = 0
    if not image_page.exists():
        raise ValueError("Image does not exist.")  # confirm this is the expected behaviour T10

    while True:
        with open("./Example3" + ext, "wb") as fd:
            image_page.download(fd)

        hash_result, img_hash = verify_hash(site, "./Example3" + ext, image_page)
        if not hash_result:
            if download_attempts >= 10:
                failed = 1
                break
            download_attempts += 1
            continue
        else:
            break
    if failed:
        raise ValueError(
            "Hash check failed for ./Example3{0} vs {1} {2} times. Aborting...".format(ext, str(image_page.title()),
                                                                                       str(download_attempts)))

    del download_attempts
    with open("./Example3" + ext, "rb") as f:
        try:
            result = image_is_corrupt(f)
        except UnidentifiedImageError:
            os.remove("./Example3" + ext)  # file not an image.
            raise
    del ext  # no longer a needed variable
    if result:  # image corrupt
        try:  # TODO: Add record to database about successful notification?
            notify_and_tag(site, image_page, calculate_difference(date_scanned))
            # notify_and_tag_for_deletion(site, image_page, username, calculate_difference(date_scanned))
        except:  # TODO: Add record to database about failed notification?
            pass
    else:  # image not corrupt
        edit_summary = "Removing [[Template:TSB image identified corrupt]] - image no longer corrupt"

        code = mwparserfromhell.parse(image_page.text)
        for template in code.filter_templates():
            if template.name.matches("TSB image identified corrupt"):
                code.remove(template)  # template no longer needed
        try:
            pwb_wrappers.retry_apierror(
                lambda:
                image_page.save(text=str(code),
                                summary=edit_summary, minor=False, botflag=True, force=True)
            )
        except pywikibot.exceptions.LockedPage as e:
            print(image_page.title())
            print(e.message)
        # update database entry to set image as no longer corrupt and nullify to_delete_nom
        update_entry(str(image_page.title()), False, None, img_hash, was_fixed=True)


def main():
    site = pywikibot.Site('commons', 'commons', user='TheSandBot')
    login_result = site.login()
    if not login_result:
        raise ValueError('Incorrect password')
    raw = get_expired_images()
    for i in raw:
        run(site, i[0], i[1], i[2], i[3])


if __name__ == '__main__':
    # main()
    pass
