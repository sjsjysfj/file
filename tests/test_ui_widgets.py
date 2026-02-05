import pytest
from PyQt6.QtWidgets import QApplication, QTableWidgetItem
from PyQt6.QtCore import Qt
from src.ui.widgets import TaskTable
import sys

# Need app instance for widgets
app = QApplication(sys.argv)

def test_task_table_checkboxes():
    table = TaskTable()
    
    # Add tasks
    table.add_task("test1.jpg", "split")
    table.add_task("test2.jpg", "split")
    
    assert table.rowCount() == 2
    
    # Check if checkbox exists and is unchecked
    item0 = table.item(0, 0)
    assert item0.checkState() == Qt.CheckState.Unchecked
    
    # Test checking
    item0.setCheckState(Qt.CheckState.Checked)
    checked = table.get_checked_rows()
    assert len(checked) == 1
    assert checked[0] == 0
    
    # Test select all
    table.set_all_check_state(Qt.CheckState.Checked)
    checked = table.get_checked_rows()
    assert len(checked) == 2
    
    # Test remove rows
    table.remove_rows([0])
    assert table.rowCount() == 1
    # The remaining item should be test2.jpg
    assert table.item(0, 1).text() == "test2.jpg"

def test_task_table_columns():
    table = TaskTable()
    assert table.columnCount() == 5
    # Verify headers roughly
    assert table.horizontalHeaderItem(0).text() == "选择"
