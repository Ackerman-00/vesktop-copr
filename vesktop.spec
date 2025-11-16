# vesktop.spec - Repackage Vesktop upstream artifacts (tarball or binary RPM)
%global debug_package %{nil}

Name:           vesktop
Version:        1.6.1
Release:        1%{?dist}
Summary:        A custom Discord Client focusing on performance, features, and customizability
License:        GPL-3.0-only AND MIT
URL:            https://github.com/Vencord/Vesktop

# Prefer upstream tarball as Source0; fallback to binary RPM in Source1.
Source0:        https://github.com/Vencord/Vesktop/releases/download/v%{version}/vesktop-%{version}.tar.gz
Source1:        https://github.com/Vencord/Vesktop/releases/download/v%{version}/vesktop-%{version}.x86_64.rpm
Source2:        %{name}.desktop

BuildArch:      x86_64

# Minimal build-time tools needed for repackaging and validation
BuildRequires:  desktop-file-utils
BuildRequires:  rpm-build

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
# Working extraction dir
rm -rf %{_tmppath}/vesktop-extract
mkdir -p %{_tmppath}/vesktop-extract
cd %{_tmppath}/vesktop-extract

# Prefer the tarball (Source0) if present; else extract the binary RPM (Source1)
if [ -f %{SOURCE0} ]; then
  tar -xzf %{SOURCE0} || { echo "Failed to extract %{SOURCE0}"; exit 1; }
  EXTRACTED_DIR=$(tar -tzf %{SOURCE0} | head -1 | sed -e 's:/$::' || true)
  if [ -n "$EXTRACTED_DIR" -a -d "$EXTRACTED_DIR" ]; then
    mv "$EXTRACTED_DIR" extracted || :
  else
    mkdir -p extracted
    cp -a ./* extracted/ 2>/dev/null || :
  fi
elif [ -f %{SOURCE1} ]; then
  rpm2cpio %{SOURCE1} | cpio -idmv || true
  if [ -d opt/Vesktop ]; then
    mkdir -p extracted
    mv opt/Vesktop extracted/Vesktop || :
  fi
else
  echo "ERROR: No upstream source found (neither tar.gz nor x86_64.rpm)."
  exit 1
fi

# Final verify
if [ ! -d %{_tmppath}/vesktop-extract/extracted ]; then
  echo "ERROR: upstream payload not found (extracted directory missing)"
  exit 1
fi

%build
# No build steps required — using prebuilt artifacts.

%install
# Standard directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
mkdir -p %{buildroot}%{_datadir}/licenses/%{name}
mkdir -p %{buildroot}/opt

# Copy app into /opt/Vesktop (preserve upstream layout)
if [ -d %{_tmppath}/vesktop-extract/extracted/Vesktop ]; then
  cp -a %{_tmppath}/vesktop-extract/extracted/Vesktop %{buildroot}/opt/ || :
else
  cp -a %{_tmppath}/vesktop-extract/extracted %{buildroot}/opt/Vesktop-tmp || :
  if [ -d %{buildroot}/opt/Vesktop-tmp/vesktop-%{version} ]; then
    mv %{buildroot}/opt/Vesktop-tmp/vesktop-%{version} %{buildroot}/opt/Vesktop || :
    rmdir %{buildroot}/opt/Vesktop-tmp || true
  else
    if find %{buildroot}/opt/Vesktop-tmp -type f -name vesktop | grep -q vesktop; then
      mkdir -p %{buildroot}/opt/Vesktop
      cp -a %{buildroot}/opt/Vesktop-tmp/* %{buildroot}/opt/Vesktop/ || :
      rm -rf %{buildroot}/opt/Vesktop-tmp || :
    else
      mv %{buildroot}/opt/Vesktop-tmp %{buildroot}/opt/Vesktop || :
    fi
  fi
fi

# Ensure vesktop binary exists
if [ ! -f %{buildroot}/opt/Vesktop/vesktop -a ! -f %{buildroot}/opt/Vesktop/vesktop.bin ]; then
  echo "ERROR: vesktop binary not found under /opt/Vesktop — aborting packaging"
  exit 1
fi

# Install wrapper if needed
if [ ! -f %{buildroot}%{_bindir}/%{name} ]; then
  cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/bash
exec /opt/Vesktop/vesktop "$@"
EOF
  chmod +x %{buildroot}%{_bindir}/%{name}
fi

# Desktop file
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{name}.desktop || :

# Icon handling
ICON_FILE=$(find %{buildroot}/opt/Vesktop -type f \( -iname '*.png' -o -iname '*.svg' \) | head -1 || true)
if [ -n "$ICON_FILE" ]; then
  install -m 644 "$ICON_FILE" %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png 2>/dev/null || \
  install -m 644 "$ICON_FILE" %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/vesktop.svg 2>/dev/null || :
fi
test -f %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png || touch %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vesktop.png

# License
if [ -d %{buildroot}/opt/Vesktop ] && ls %{buildroot}/opt/Vesktop/LICENSE* &>/dev/null; then
  cp -a %{buildroot}/opt/Vesktop/LICENSE* %{buildroot}%{_datadir}/licenses/%{name}/ 2>/dev/null || :
else
  echo "GPL-3.0-only AND MIT - See https://github.com/Vencord/Vesktop for details" > %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
fi

# Validate desktop file (non-fatal)
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
- Fixed parsing issue by removing inline BuildRequires comments and normalized Source ordering.
- Repackage upstream artifacts: support tarball and binary RPM payloads.
- Install app under /opt/Vesktop, provide /usr/bin/vesktop wrapper.
- Add robust icon and license handling and fail-fast checks.

