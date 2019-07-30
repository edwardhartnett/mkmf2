import os
import sys
import datetime
import textwrap
#import pdb; pdb.set_trace()

config_fragment = open("configure.fragment", "w+")
for dirname, subdirs, files in os.walk(sys.argv[1]):
    if '/.git' not in dirname:
        print 'dirname '+ dirname

        # If this is the main directory, it will include .git in the
        # subdir list. Remove it.
        try:
            subdirs.remove(".git")
        except Exception:
            pass

        # Create Makefile.am.
        f = open(os.path.join(dirname, "Makefile.am"),"w+")

        # Makefile.am header.
        f.write("# This is an automake file for the GFDL AM4 model.\n")
        f.write("# This builds directory " + dirname + ".\n")
        f.write("#\n")
        f.write("# Ed Hartnett " + datetime.datetime.now().strftime("%Y-%m-%d") + "\n\n")

        # SUBDIRS primary.
        if subdirs:
            my_subdirs = " ".join(subdirs)
            f.write("# Run make targets in each of these subdirs\n")
            f.write('SUBDIRS = ' + my_subdirs + "\n\n")

        # Add this to list for AC_CONFIG_FILES in configure.ac.
        if dirname != ".":
            config_fragment.write("        " + dirname[2:] + "/Makefile\n")

        # Create a list of F90 modules to be built in this dir.
        my_mods = []

        # Handle each file.
        for filename in files:
            if ".F90" in filename:
                print '    filename ' + filename
                my_mods.append(filename[:-4])
            # with open(os.path.join(dirname, filename), 'r') as src:
            #     dest.write(src.read())

        # Deal the F90 modules.
        if my_mods:
            # Find the mod file names of all the .F90 files in this dir.
            modfiles = [s + "_mod.mod " for s in my_mods]

            # Find the names of the convenience libraries.
            libfiles = ["lib" + s + ".la " for s in my_mods]

            # Build these uninstalled convenience libraries.
            f.write("# Build these uninstalled convenience libraries.\n")
            f.write("noinst_LTLIBRARIES = " + " \\\n".join(textwrap.wrap("".join(libfiles), 70)) + "\n")
            f.write("\n")

            # Each convenience library depends on its source.
            f.write("# Each convenience library depends on its source.\n")
            for mf in my_mods:
                f.write("lib" + mf + "_la_SOURCES = " + mf + ".F90\n")
            f.write("\n")

            # Each mod file depends on the .o file.
            f.write("# Each mod file depends on the .o file.\n")
            for mf in my_mods:
                f.write(mf + "_mod.mod: " + mf + ".$(OBJEXT)\n")
            f.write("\n")

            # Insert these comments to guide later work.
            f.write("# Some mods are dependant on other mods in this dir.\n")
            f.write("#mpp_data.$(OBJEXT): mpp_parameter_mod.mod\n")
            f.write("\n")

            # Write the MODFILES line(s).
            f.write("# Mod files are built and then installed as headers.\n")
            wrapped_modfiles = textwrap.wrap("".join(modfiles), 70)
            print("wrapped MODFILES = " + " \\\n".join(wrapped_modfiles) + "\n")
            f.write("MODFILES = " + " \\\n".join(wrapped_modfiles) + "\n")
            f.write("include_HEADERS = $(MODFILES)\n")
            f.write("BUILT_SOURCES = $(MODFILES)\n")

            # Finish the Makefile.am.
            f.write("\n")
            f.write("CLEANFILES = *.mod\n")

        f.close()

config_fragment.close()
