from flask_principal import Permission, RoleNeed

admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(RoleNeed('user'))

