import os
import sys
import datetime
import textwrap
#import pdb; pdb.set_trace()

ignore = ['.git', 'autom4te.cache', 'm4', '.libs']

# This will get a list of files for AC_CONFIG_OUTPUT, in a temp file
# called configure.fragment.
config_fragment = open("configure.fragment", "w+")

# Recurse through the directories.
for dirname, subdirs, files in os.walk(sys.argv[1]):
    if not any(x in dirname for x in ignore):
        print 'dirname '+ dirname

        # Remove directories which should be ignored.
        for x in ignore:
            try:
                subdirs.remove(x)
            except Exception:
                pass

        # Create Makefile.am.
        f = open(os.path.join(dirname, "Makefile.am"), "w+")

        # Makefile.am header.
        f.write("# This is an automake file for the GFDL AM4 model.\n")
        f.write("# This builds directory " + dirname + ".\n")
        f.write("#\n")
        f.write("# Ed Hartnett " + datetime.datetime.now().strftime("%Y-%m-%d") + "\n\n")

        if dirname == '.':
            f.write("# This directory stores libtool macros, put there by aclocal.\n")
            f.write("ACLOCAL_AMFLAGS = -I m4\n")
            f.write("\n")

        # SUBDIRS primary.
        if subdirs:
            my_subdirs = " ".join(subdirs)
            f.write("# Run make targets in each of these subdirs\n")
            f.write('SUBDIRS = ' + my_subdirs + "\n\n")

        # Add this to list for AC_CONFIG_FILES in configure.ac.
        if dirname != ".":
            config_fragment.write("        " + dirname[2:] + "/Makefile\n")

        # Create a list of F90 modules to be built in this dir. Some
        # filenames have dots in them, just to be special. To change
        # the dots to underscore, use .replace().
        my_mods = []
        extra_dist = []

        # Handle each file.
        for filename in files:
            if ".F90" in filename:
                print '    filename ' + filename
                my_mods.append(filename[:-4])
            elif any(x in filename for x in [".inc", ".h", ".pdf", ".ps"]):
                print '    filename ' + filename
                extra_dist.append(filename)

        # Deal the F90 modules.
        if my_mods:
            # Find the mod file names of all the .F90 files in this dir.
            modfiles = [s.replace(".", "_") + "_mod.mod " for s in my_mods]

            # Find the names of the convenience libraries.
            libfiles = ["lib" + s.replace(".", "_") + ".la " for s in my_mods]

            # Build these uninstalled convenience libraries.
            f.write("# Build these uninstalled convenience libraries.\n")
            f.write("noinst_LTLIBRARIES = " + " \\\n".join(textwrap.wrap("".join(libfiles), 70)) + "\n")
            f.write("\n")

            # Each convenience library depends on its source.
            f.write("# Each convenience library depends on its source.\n")
            for mf in my_mods:
                f.write("lib" + mf.replace(".", "_") + "_la_SOURCES = " + mf + ".F90\n")
            f.write("\n")

            # Each mod file depends on the .o file.
            f.write("# Each mod file depends on the .o file.\n")
            for mf in my_mods:
                f.write(mf + "_mod.mod: " + mf + ".$(OBJEXT)\n")
            f.write("\n")

            # Check each mod to see if it is used by others in this dir.
            f.write("# Some mods are dependant on other mods in this dir.\n")
            for mf in my_mods:
                uses = []
                whole_file = open(os.path.join(dirname, mf + ".F90")).read()
                for mf2 in my_mods:
                    if mf2 != mf:
                        #print "checking whether " + mf2 + " is used by " + mf
                        if "use " + mf2 in whole_file:
                            uses.append(mf2.replace(".", "_") + "_mod.mod")

                # If mf uses any other mods, add that to Makefile.am
                if uses:
                    f.write(mf + ".$(OBJEXT): " + " ".join(uses) + "\n")
            f.write("\n")

            # Write the MODFILES line(s).
            f.write("# Mod files are built and then installed as headers.\n")
            wrapped_modfiles = textwrap.wrap("".join(modfiles), 70)
            print("wrapped MODFILES = " + " \\\n".join(wrapped_modfiles) + "\n")
            f.write("MODFILES = " + " \\\n".join(wrapped_modfiles) + "\n")
            f.write("include_HEADERS = $(MODFILES)\n")
            f.write("BUILT_SOURCES = $(MODFILES)\n")
            f.write("\n")

            # Add extra_dist files.
            my_extra_dist = " \\\n".join(textwrap.wrap(" ".join(extra_dist), 70))
            f.write("EXTRA_DIST = " + my_extra_dist + "\n")
            print("EXTRA_DIST = " + my_extra_dist + "\n")
            f.write("\n")

            # Finish the Makefile.am.
            f.write("CLEANFILES = *.mod\n")

        f.close()

config_fragment.close()
