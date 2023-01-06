def detect_user(user):
    if user.role == 1:
        redirectUrl = 'vendorHome'
        return redirectUrl
    if user.role == 2:
        redirectUrl = 'userHome'
        return redirectUrl
    if user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl