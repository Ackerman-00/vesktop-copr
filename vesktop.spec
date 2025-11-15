# vesktop.spec - RPM Passthrough Method

# Package metadata
Name:           vesktop
Version:        %__version__
Release:        1%{?dist}
Summary:        A custom Discord Client focusing on performance, features, and customizability.
License:        GPL-3.0-only AND MIT
URL:            https://github.com/Vencord/Vesktop

# Source0 is now the official upstream RPM
Source0:        https://github.com/Vencord/Vesktop/releases/download/v%{version}/vesktop-%{version}.x86_64.rpm
Source1:        %{name}.desktop
# Dependencies
# We don't need BuildRequires since we aren't compiling anything
Requires:       libappindicator-gtk3

%description
Vesktop is an open-source, custom Discord client based on Electron, designed for
users who want enhanced features, better performance, and deep customization 
through the Vencord client mod.

%prep
# No need to unpack, the RPM is our source

%build
# Nothing to build

%install
# Unpack the contents of the upstream RPM into our build root
/usr/bin/rpm2cpio %{SOURCE0} | cpio -idmv -D %{buildroot}

# Install the custom desktop file (Source1) for full integration
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license /usr/share/vesktop/LICENSE
# Automatically grab all files from the unpacked RPM
%{_bindir}/*
%{_datadir}/%{name}/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/*/*/*/%{name}.png

%changelog
* Sat Nov 15 2025 Quietcraft <mdzunaid384@gmail.com> - v1.6.1-1.20251116003339427319.main.3.g0e426db
- Final corrected SPEC and Packit config (Quietcraft)
- Switched to using official upstream RPM as Source0 (Quietcraft)
- Final corrected SPEC and Packit config (Quietcraft)

* Sat Nov 15 2024 Your Name <you@example.com> - %__version__-1
- Switched to using official upstream RPM binary for package source.
