export SB_TOP=$(shell pwd)
export BUILD_TOP=$(SB_TOP)/build

all: python-web-proxy-deb static-web-proxy-deb web-proxy-init-deb

env: 
	@if [ ! -d $(BUILD_TOP) ]; then mkdir $(BUILD_TOP); fi

python-web-proxy-deb: env
	$(eval PKGNAME=$(subst -deb,,$@))
	$(eval BUILDDIR=$(BUILD_TOP)/$(PKGNAME))
	if [ ! -d $(BUILDDIR) ]; then mkdir $(BUILDDIR); fi
	cp setup.py $(BUILDDIR)
	cp -r web_proxy $(BUILDDIR)
	cp -r packages/$(PKGNAME)/debian $(BUILDDIR)
	cd $(BUILDDIR); fakeroot debian/rules binary

static-web-proxy-deb: env
	$(eval PKGNAME=$(subst -deb,,$@))
	$(eval BUILDDIR=$(BUILD_TOP)/$(PKGNAME))
	if [ ! -d $(BUILDDIR) ]; then mkdir $(BUILDDIR); fi
	cp -r packages/$(PKGNAME)/debian $(BUILDDIR)
	cd $(BUILDDIR); fakeroot debian/rules binary

web-proxy-init-deb: env
	$(eval PKGNAME=$(subst -deb,,$@))
	$(eval BUILDDIR=$(BUILD_TOP)/$(PKGNAME))
	if [ ! -d $(BUILDDIR) ]; then mkdir $(BUILDDIR); fi
	cp -r packages/$(PKGNAME)/debian $(BUILDDIR)
	cd $(BUILDDIR); fakeroot debian/rules binary



clean:
	rm -rf $(BUILD_TOP)
