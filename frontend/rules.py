import rules
from members.rules import is_organization_admin

rules.add_perm("frontend", is_organization_admin)
