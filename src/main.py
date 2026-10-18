# Copyright (C) 2026 Titomfun (TitomfunDev)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from ui.app import MainLauncherWindow
from core import auth, instances, updater
from core.instances import DeprecatedFeatureError

try:
    from core.version import INTERNAL_TAG
except ImportError:
    INTERNAL_TAG = "v0.0.0-dev"

app = QApplication(sys.argv)

QMessageBox.warning(
        None,
        "Version",
        f"{INTERNAL_TAG}"
    )  

updater.check_and_update()

if auth.get_valid_session() is None :
    auth.login()

try:
    instances.sync_and_get_manifest()
except DeprecatedFeatureError as e:
    QMessageBox.warning(
        None,
        "Deprecated Feature",
        f"Warning!\n{e}\nPlease update your launcher as this feature will stop working soon."
    )  


window = MainLauncherWindow()
window.show()
sys.exit(app.exec())