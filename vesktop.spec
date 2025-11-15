Name:           vesktop
Version:        %{version}
Release:        1%{?dist}
Summary:        A custom Discord Client focusing on performance, features, and customizability.

License:        GPL-3.0-only AND MIT
URL:            https://github.com/Vencord/Vesktop
Source0:        https://github.com/Vencord/Vesktop/releases/download/v%{version}/vesktop-%{version}.tar.gz
Source1:        %{name}.desktop

Requires:       libappindicator-gtk3

%description
Vesktop is an open-source, custom Discord client based on Electron, designed for
users who want enhanced features, better performance, and deep customization
through the Vencord client mod.

%prep
# Setup the build directory and extract the upstream tarball.
%setup -q -n vesktop-%{version}

%build
# Nothing to build as we are packaging a pre-built Electron application.

%install
# Create essential directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps

# Copy the extracted application files. Adjust if the tarball structure differs.
cp -r . %{buildroot}%{_datadir}/%{name}/

# Install the executable wrapper script
cat > %{buildroot}%{_bindir}/%{name} << 'EOF'
#!/bin/bash
exec /usr/share/%{name}/%{name} "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

# Install the desktop file
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/applications/

# Install the icon (assuming it's included in the tarball)
# If the icon has a different name or path, you MUST update this line.
install -m 644 %{buildroot}%{_datadir}/%{name}/vesktop.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/ 2>/dev/null || :

# Validate the desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/256x256/apps/vesktop.png

%changelog
* Sat Nov 16 2024 Quietcraft <mdzunaid384@gmail.com> - %{version}-1
- Fixed Source0 to use the correct tarball.
- Rewrote %install section to properly handle tarball extraction.
- Corrected file paths and added an executable wrapper.
- Using %{version} macro for automatic version updates by Packit.
