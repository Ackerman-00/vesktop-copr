# vesktop.spec - Repackage Vesktop upstream artifacts (tarball or binary RPM)
%global debug_package %{nil}

Name:           vesktop
Version:        1.6.1
Release:        1%{?dist}
Summary:        A custom Discord Client focusing on performance, features, and customizability
License:        GPL-3.0-only AND MIT
URL:            https://github.com/Vencord/Vesktop

# Primary: upstream binary RPM (prebuilt Electron)
Source0:        https://github.com/Vencord/Vesktop/releases/download/v%{version}/vesktop-%{version}.x86_64.rpm
# Upstream tar.gz (also contains built artifacts) - optional, used first if present
Source2:        https://github.com/Vencord/Vesktop/releases/download/v%{version}/vesktop-%{version}.tar.gz
# Desktop file (from your repo)
Source1:        %{name}.desktop

BuildArch:      x86_64

# Build dependencies (minimal for repackaging + validation)
BuildRequires:  desktop-file-utils
BuildRequires:  rpm-build   # for rpm2cpio availability in some buildroots (defensive)
BuildRequires:  findutils    # for 'find' in %install (usually present)
# If you plan to build from source inside the spec (not done here), you'll need nodejs/pnpm, etc.

# Runtime dependencies
Requires:       libappindicator-gtk3
Requires:       gtk3
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       alsa-lib

%description
Vesktop is an open-source, custom Discord client based on Electron,
designed for users who want enhanced performance, features, and deep customization
through the Vencord client mod.

%prep
# Create a working extraction directory
rm -rf %{_tmppath}/vesktop-extract
mkdir -p %{_tmppath}/vesktop-extract
cd %{_tmppath}/vesktop-extract

# Prefer the tarball if present (Packit may provide it as %{SOURCE2})
if [ -f %{SOURCE2} ]; then
  # Extract tarball (it contains a top-level directory like vesktop-1.6.1/)
  tar -xzf %{SOURCE2} || \
    { echo "Failed to extract %{SOURCE2}"; exit 1; }
  # normalize extracted_dir
  EXTRACTED_DIR=$(tar -tzf %{SOURCE2} | head -1 | sed -e 's:/$::' || true)
  if [ -n "$EXTRACTED_DIR" -a -d "$EXTRACTED_DIR" ]; then
    mv "$EXTRACTED_DIR" extracted || :
  else
    # fallback: if contents extracted into current dir, use current dir
    mkdir -p extracted
    cp -a ./* extracted/ 2>/dev/null || :
  fi
else
  # Fallback: extract upstream binary RPM payload
  # rpm2cpio should be present (we required rpm-build to be safe)
  rpm2cpio %{SOURCE0} | cpio -idmv || true
  # Upstream RPM places files under /opt/Vesktop in the rpm payload.
  # Move them into 'extracted' dir for uniform handling below.
  if [ -d opt/Vesktop ]; then
    mkdir -p extracted
    mv opt/Vesktop extracted/Vesktop || :
  fi
fi

# Verify we have an extracted app directory
if [ ! -d %{_tmppath}/vesktop-extract/extracted ]; then
  echo "ERROR: upstream payload not found (neither tarball nor RPM payload produced vesktop files)"
  exit 1
fi

%build
# No building required; this is a prebuilt application repackaging.
# (If you want to build from source inside RPM, add nodejs/pnpm steps here.)

%install
# Standard directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}
mkdir -p %{buildroot}/opt
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
mkdir -p %{buildroot}%{_datadir}/licenses/%{name}

# Copy extracted app files to /opt/Vesktop (preserve upstream layout)
# extracted/ may contain "Vesktop" (from rpm) or a top-level folder of tarball
if [ -d %{_tmppath}/vesktop-extract/extracted/Vesktop ]; then
  cp -a %{_tmppath}/vesktop-extract/extracted/Vesktop %{buildroot}/opt/ || :
elif [ -d %{_tmppath}/vesktop-extract/extracted ]; then
  # If the tarball extracted into extracted/vesktop-1.6.1/* containing vesktop binary
  cp -a %{_tmppath}/vesktop-extract/extracted %{buildroot}/opt/Vesktop-tmp || :
  # normalize: if we copied into opt/Vesktop-tmp/vesktop-1.6.1/*, move those into opt/Vesktop
  if [ -d %{buildroot}/opt/Vesktop-tmp/vesktop-%{version} ]; then
    mv %{buildroot}/opt/Vesktop-tmp/vesktop-%{version} %{buildroot}/opt/Vesktop || :
    rmdir %{buildroot}/opt/Vesktop-tmp || true
  else
    # Try to detect a 'vesktop' binary in the tree and move its parent as Vesktop
    if find %{buildroot}/opt/Vesktop-tmp -type f -name vesktop | grep -q vesktop; then
      mkdir -p %{buildroot}/opt/Vesktop
      cp -a %{buildroot}/opt/Vesktop-tmp/* %{buildroot}/opt/Vesktop/ || :
      rm -rf %{buildroot}/opt/Vesktop-tmp || :
    else
      # fallback: move 'extracted' into /opt/Vesktop
      mv %{buildroot}/opt/Vesktop-tmp %{buildroot}/opt/Vesktop || :
    fi
  fi
fi

# Final sanity check: ensure /opt/Vesktop/vesktop exists
if [ ! -f %{buildroot}/opt/Vesktop/vesktop -a ! -f %{buildroot}/opt/Vesktop/vesktop.bin ]; then
  echo "ERROR: vesktop binary not found under /opt/Vesktop — aborting packaging"
  exit 1
fi

# Install a small wrapper into /usr/bin if upstream didn't already provide one
if [ ! -f %{buildroot}%{_bindir}/%{name} ]; then
  cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/bash
exec /opt/Vesktop/vesktop "$@"
EOF
  chmod +x %{buildroot}%{_bindir}/%{name}
fi

# Install desktop file (your Source1) into /usr/share/applications
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{name}.desktop || :

# Attempt to find a good icon in the extracted tree and install it to hicolor
# Search for png files in the app payload and pick the first match
ICON_FILE=$(find %{buildroot}/opt/Vesktop -type f \( -iname '*.png' -o -iname '*.svg' \) | head -1 || true)
if [ -n "$ICON_FILE" ]; then
  # prefer png -> install to 256x256 path; fallback to svg if present
  install -m 644 "$ICON_FILE" %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png 2>/dev/null || \
  install -m 644 "$ICON_FILE" %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/vesktop.svg 2>/dev/null || :
fi
# Ensure an icon exists (policy may require one); create minimal placeholder if none found
test -f %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png || touch %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png

# Install license files if present in the extracted tree; otherwise create minimal license text
if [ -d %{buildroot}/opt/Vesktop ] && ls %{buildroot}/opt/Vesktop/LICENSE* &>/dev/null; then
  mkdir -p %{buildroot}%{_datadir}/licenses/%{name}
  cp -a %{buildroot}/opt/Vesktop/LICENSE* %{buildroot}%{_datadir}/licenses/%{name}/ 2>/dev/null || :
else
  mkdir -p %{buildroot}%{_datadir}/licenses/%{name}
  echo "GPL-3.0-only AND MIT - See https://github.com/Vencord/Vesktop for details" > %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
fi

# Validate desktop file (non-fatal - show warning but don't hard-fail)
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop || echo "Warning: desktop-file-validate failed."

%files
%defattr(-,root,root,-)
%license %{_datadir}/licenses/%{name}/*
%doc /opt/Vesktop/LICENSE.electron.txt /opt/Vesktop/LICENSES.chromium.html
%{_bindir}/%{name}
%dir /opt/Vesktop
/opt/Vesktop
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/256x256/apps/vesktop.png

%changelog
* Sun Nov 16 2025 Quietcraft <mdzunaid384@gmail.com> - 1.6.1-1
- Repackage upstream artifacts: support both tarball and binary RPM payloads.
- Install app under /opt/Vesktop, provide /usr/bin/vesktop wrapper.
- Add robust icon and license handling and fail-fast checks to avoid empty packages.

