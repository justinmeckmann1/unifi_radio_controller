from toggle_ap import toggleAP

# UniFi Controller Details
config = {
    'base_url': "https://192.168.0.1",
    'username': "api",
    'password': "6U8ko9NXaojxxhLAdmLhRkwFs4oqY3eMNkFRAEBJH8rupwMBqU",
    'site_id' : "default" 
}

if __name__ == '__main__':
    toggleAP(config, ap='U6+ Justin', action='on')