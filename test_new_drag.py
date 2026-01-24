import pytest
from pathlib import Path
from PySide6.QtCore import Qt

from main import TextEditor


class TestDragTabWithMultipleTabs:
    """Test for dragging tabs between panes when both have multiple tabs."""

    def test_drag_tab_from_pane_with_fewer_tabs(self, qtbot, tmp_path):
        """Test dragging tab from pane that has fewer tabs than the destination pane.
        
        This is a regression test for the bug where tabs couldn't be dragged between
        views when the source pane had fewer tabs than the destination pane. The issue
        was that the source pane lookup only checked if the tab index existed in a pane,
        so it would incorrectly match the destination pane instead of the source pane.
        
        Scenario:
        - pane1 has 2 tabs (indices 0, 1)
        - pane2 has 3 tabs (indices 0, 1, 2)
        - When dragging tab 1 from pane1, the code would check:
          - pane1: count=2 > index=1? YES (correct match)
          - (stops here, but the bug would be if pane2 was checked first)
        - However, the real bug is when the source pane is checked AFTER a pane
          that has more tabs, it gets skipped due to order dependency.
        """
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"
        file4 = tmp_path / "file4.txt"
        file5 = tmp_path / "file5.txt"
        
        file1.write_text("content1")
        file2.write_text("content2")
        file3.write_text("content3")
        file4.write_text("content4")
        file5.write_text("content5")
        
        # Create pane2 first with 3 tabs
        window.add_split_view()
        pane2 = window.active_pane
        window.load_file(str(file3))
        window.load_file(str(file4))
        window.load_file(str(file5))
        
        # Now set pane1 as active and open only 1 file
        # This is tricky - we need to navigate back to pane1
        pane1 = window.split_panes[0]
        window.set_active_pane(pane1)
        window.load_file(str(file1))
        
        # Verify initial state
        assert pane1.tab_widget.count() == 1  # file1
        assert pane2.tab_widget.count() == 3  # file3, file4, file5
        
        # Now drag a new tab to pane1
        window.set_active_pane(pane1)
        window.load_file(str(file2))
        
        assert pane1.tab_widget.count() == 2  # file1, file2
        
        # Debug: print open_files before drag
        print(f"\nBefore drag:")
        print(f"pane1 tabs: {[pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]}")
        print(f"pane2 tabs: {[pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]}")
        print(f"open_files: {window.open_files}")
        
        # Simulate dragging tab at index 1 (file2) from pane1 to pane2
        window.on_tab_dropped_to_pane("tab:1", pane2)
        
        # Debug: print state after drag
        print(f"\nAfter drag:")
        print(f"pane1 tabs: {[pane1.tab_widget.tabText(i) for i in range(pane1.tab_widget.count())]}")
        print(f"pane2 tabs: {[pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]}")
        print(f"open_files: {window.open_files}")
        
        # Verify file2 was moved from pane1 to pane2
        assert pane1.tab_widget.count() == 1, f"pane1 should have 1 tab, has {pane1.tab_widget.count()}"
        assert pane2.tab_widget.count() == 4, f"pane2 should have 4 tabs, has {pane2.tab_widget.count()}"
        
        # Verify the content is correct
        pane2_tabs_after = [pane2.tab_widget.tabText(i) for i in range(pane2.tab_widget.count())]
        assert any("file2.txt" in text for text in pane2_tabs_after), "file2 should be in pane2 after drag"
