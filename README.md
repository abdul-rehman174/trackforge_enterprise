# TrackForge Enterprise

An inventory and procurement management system built with Django 5.

## Features

- **Inventory** — products, categories, multi-warehouse stock, audit trail of every movement
- **Procurement** — suppliers, purchase orders with line items, partial / full receiving that updates stock automatically, status transitions (draft → submitted → partial → completed)
- **Accounts** — custom user model with role-based permission groups (admin, manager, staff, user) and self-service signup
- **Dashboard** — real-time counts, low-stock alerts with one-click reorder
- Unified theme: every page shares one base template, one CSS file, and a sidebar that auto-highlights the active section

## Stack

- Django 5.1 · Python 3.12+ · SQLite (dev) — drop in Postgres for production by changing `DATABASES`
- Vanilla CSS, Font Awesome 6, no JS framework

## Quick start

```bash
# 1. Clone and enter
git clone <your-fork-url> trackforge_enterprise
cd trackforge_enterprise

# 2. Virtual env + install
python3 -m venv enterprise_env
source enterprise_env/bin/activate
pip install -r requirements.txt

# 3. Migrate the DB
python trackforge/manage.py migrate

# 4. Provision the role groups (admin / manager / staff / user)
python trackforge/manage.py setup_groups

# 5. Create your first superuser
python trackforge/manage.py createsuperuser

# 6. Run
python trackforge/manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

## Roles & permissions

`accounts/management/commands/setup_groups.py` provisions four groups:

| Role    | Apps                       | Actions                  |
|---------|----------------------------|--------------------------|
| admin   | accounts, inventory, procurement | add, change, delete, view |
| manager | accounts, inventory, procurement | add, change, view        |
| staff   | inventory, procurement     | add, change, view        |
| user    | accounts, inventory, procurement | view only                |

A `post_save` signal auto-assigns each new user to the group matching their `role`. Self-signups always land in `user`; promote via the Django admin.

## Configuration

Settings read these env vars (with safe dev defaults):

| Variable               | Default                                 |
|------------------------|-----------------------------------------|
| `DJANGO_SECRET_KEY`    | insecure dev key (override in prod)     |
| `DJANGO_DEBUG`         | `True`                                  |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` (comma-separated) |

When `DJANGO_DEBUG=False`, HSTS, secure cookies, and `X-Frame-Options: DENY` are turned on automatically.

## Project layout

```
trackforge/
├── accounts/        # CustomUser, role groups, signup/login/logout
├── core/            # AuditableModel mixin, dashboard view
├── inventory/       # Product, Category, Warehouse, Stock, StockTransaction
├── procurement/     # Supplier, PurchaseOrder, POLineItem, receive flow
├── static/css/      # main.css — single source of truth for styling
├── templates/       # base.html + per-app pages, all extending base
└── trackforge/      # settings, root urls, wsgi
```

## License

Internal project — no license declared.
