#
# Ginger
#
# Copyright IBM Corp, 2014-2016
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

SUBDIRS= po control model ui contrib tests

ginger_PYTHON = $(wildcard *.py)

AUTOMAKE_OPTIONS = foreign

ACLOCAL_AMFLAGS = --install -I m4

PEP8_WHITELIST = \
	control \
	model \
	tests\
	$(NULL)

gingerdir = $(pythondir)/wok/plugins/ginger

confdir = $(sysconfdir)/wok/plugins.d
dist_conf_DATA = ginger.conf

EXTRA_DIST = \
	API.json \
	VERSION \
	autogen.sh \
	build-aux/config.rpath \
	build-aux/pkg-version \
	$(NULL)

CLEANFILES = ginger.spec `find "$(top_srcdir)" -type f -name "*.pyc" -print`

I18N_FILES = ./i18n.py \
        $(NULL)

# '4b825dc642cb6eb9a060e54bf8d69288fbee4904' is the hash of an empty
# Git tree calculated by:
# $ git hash-object -t tree /dev/null
check-local:
	contrib/check_i18n.py $(I18N_FILES)
	@if [ -d '.git' ]; then                                        \
		find . -path './.git' -prune -o                        \
			-name '*.py' -o -name '*.py.in'  |             \
			xargs $(PYFLAKES) |                            \
			while read LINE; do echo "$$LINE"; false; done \
	else                                                           \
		find . -name '*.py' -o -name '*.py.in'  |              \
			xargs $(PYFLAKES) |                            \
			while read LINE; do echo "$$LINE"; false; done \
	fi
	$(PEP8) --version
	$(PEP8) --filename '*.py,*.py.in' $(PEP8_WHITELIST)
	@if $(GIT) rev-parse &> /dev/null ; then                          \
		echo "Whitespace verification ...";                       \
		$(GIT) diff --check ;                                     \
		$(GIT) diff-tree --check                                  \
			'4b825dc642cb6eb9a060e54bf8d69288fbee4904' HEAD ; \
		echo "IBM copyright year verification ..." ;               \
		/bin/bash ../../../../check-IBM-license-header.sh ;       \
	fi
	@echo "Ok"

#
# Packaging helpers
#
install-deb: install
	cp -R $(top_srcdir)/contrib/DEBIAN $(DESTDIR)/

deb: contrib/make-deb.sh
	$(top_srcdir)/contrib/make-deb.sh


# Link built mo files in the source tree to enable use of translations from
# within the source tree
all-local:
	while read L && test -n "$$L"; do                  \
		dir=mo/$$L/LC_MESSAGES ;                       \
		$(MKDIR_P) $$dir ;                             \
		ln -sf ../../../po/$$L.gmo $$dir/ginger.mo ;   \
	done < po/LINGUAS


install-data-local:
	@if test -d "$(systemdsystemunitdir)" ; then \
		mkdir -p $(DESTDIR)/etc/systemd/system/wokd.service.d; \
		if test -f /etc/debian_version; then \
			$(INSTALL_DATA) contrib/gingerd.service.ubuntu $(DESTDIR)/etc/systemd/system/wokd.service.d/ginger.conf; \
		else \
			$(INSTALL_DATA) contrib/gingerd.service.fedora $(DESTDIR)/etc/systemd/system/wokd.service.d/ginger.conf; \
		fi; \
	fi; \
	$(MKDIR_P) $(DESTDIR)$(gingerdir)
	$(INSTALL_DATA) API.json $(DESTDIR)$(gingerdir)/API.json


uninstall-local:
	@if test -f $(DESTDIR)/etc/systemd/system/wokd.service.d/ginger.conf; then \
		$(RM) $(DESTDIR)/etc/systemd/system/wokd.service.d/ginger.conf; \
	fi;

ginger.spec: contrib/ginger.spec.fedora contrib/ginger.spec.suse
	@if test -e /etc/redhat-release; then					\
        ln -sf contrib/ginger.spec.fedora $@ ;                  \
    elif test -e /etc/SuSE-release; then                    \
        ln -sf contrib/ginger.spec.suse $@ ;                    \
    else                                                    \
        echo "Unable to select a spec file for RPM build" ;     \
        /bin/false ;                                            \
    fi

rpm: dist ginger.spec
	$(MKDIR_P) rpm/BUILD rpm/RPMS rpm/SOURCES rpm/SPECS rpm/SRPMS
	cp $(top_srcdir)/ginger.spec rpm/SPECS/ginger.spec
	cp $(DIST_ARCHIVES) rpm/SOURCES
	rpmbuild -ba --define "_topdir `pwd`/rpm" rpm/SPECS/ginger.spec

fedora-rpm: contrib/kimchi.spec.fedora
	ln -sf contrib/ginger.spec.fedora ginger.spec
	$(MAKE) rpm

suse-rpm: contrib/kimchi.spec.suse
	ln -sf contrib/ginger.spec.suse ginger.spec
	$(MAKE) rpm

ChangeLog:
	@if $(GIT) rev-parse &> /dev/null ; then                     \
		$(top_srcdir)/build-aux/genChangelog --release > $@; \
	fi


VERSION:
	@if $(GIT) rev-parse &> /dev/null ; then                  \
		git describe --abbrev=0 --always > $@;            \
	fi


clean-local:
	rm -rf rpm


.PHONY: rpm fedora-rpm suse-rpm VERSION
