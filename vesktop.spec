Name:           vesktop
Version:        %__version__ 
Release:        1%{?dist}
Summary:        A custom Discord Client focusing on performance, features, and customizability.
License:        GPL-3.0-only AND MIT
URL:            https://github.com/Vencord/Vesktop



Source0:        %{name}-%{version}-linux-x64.tar.gz
Source1:        %{name}.desktop

# Dependencies
BuildRequires:  desktop-file-utils
Requires:       libappindicator-gtk3

%description
Vesktop is an open-source, custom Discord client based on Electron, designed for
users who want enhanced features, better performance, and deep customization 
through the Vencord client mod.

%prep
%setup -q -n vesktop-linux-x64

%build


%install
# Create directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps

# 1. Install the main application files
mv * %{buildroot}%{_datadir}/%{name}/

# 2. Create a symlink to the main executable
ln -s %{_datadir}/%{name}/vesktop %{buildroot}%{_bindir}/%{name}

# 3. Install the Desktop file (Source1)
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

# 4. Install the Icon
install -m 644 %{buildroot}%{_datadir}/%{name}/vesktop.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

%changelog
* Sat Nov 15 2024 Your Name <you@example.com> - %__version__-1
- Initial COPR package build using Packit.
