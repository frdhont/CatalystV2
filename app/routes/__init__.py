from flask import jsonify, render_template
from catalyst.reporting import get_migration_dashboard
from app import app
from catalyst.models import Entity, GoLive
from flask_login import current_user, login_required


@app.route('/')
@app.route('/index')
@login_required
def index():

    golives = GoLive.query.filter_by(customer_id=current_user.customer)
    golive_count = golives.count()

    allowed_golives = [gl.id for gl in golives]
    entity_count = Entity.query.filter(Entity.golive.in_(allowed_golives)).count()

    try:
        dashboard, labels, legacy_values, scope_values, loadfile_values, issues_values = get_migration_dashboard(current_user.customer)
    except TypeError:
        dashboard_available = False

    if dashboard.empty:
        dashboard_available = False


    return render_template('index.html', nbar='index', **locals())