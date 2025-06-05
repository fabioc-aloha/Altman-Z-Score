import matplotlib
matplotlib.use("Agg")
import pytest
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from matplotlib.testing.decorators import image_comparison
from altman_zscore.plotting_helpers import (
    make_zone_bands,
    add_zone_labels,
    make_legend_elements,
    save_plot_with_legend,
)

@pytest.fixture
def test_thresholds():
    return {"distress_zone": 1.23, "safe_zone": 2.9}

@pytest.fixture
def mock_figure():
    fig, ax = plt.subplots()
    return fig, ax

def test_make_zone_bands(mock_figure, test_thresholds):
    fig, ax = mock_figure
    ymin, ymax = 0, 5
    make_zone_bands(ax, ymin, ymax, test_thresholds)
    
    # Check that we have 3 spans (distress, grey, safe zones)
    assert len(ax.patches) == 3
    
    # Check colors and alpha values
    assert ax.patches[0].get_facecolor() == (1, 0.4, 0.4, 0.8)  # Red with alpha
    assert ax.patches[1].get_facecolor() == (0.8, 0.8, 0.8, 0.6)  # Grey with alpha
    assert ax.patches[2].get_facecolor() == (0.4, 1, 0.4, 0.5)  # Green with alpha

def test_make_zone_bands_edge_cases(mock_figure):
    fig, ax = mock_figure
    ymin, ymax = -1, 1  # Test with negative values
    thresholds = {"distress_zone": -0.5, "safe_zone": 0.5}
    make_zone_bands(ax, ymin, ymax, thresholds)
    
    # Check that we have 3 spans even with negative values
    assert len(ax.patches) == 3
    
    # Check y-coordinates
    assert ax.patches[0].get_bbox().y0 == -1
    assert ax.patches[0].get_bbox().y1 == -0.5
    assert ax.patches[1].get_bbox().y0 == -0.5
    assert ax.patches[1].get_bbox().y1 == 0.5
    assert ax.patches[2].get_bbox().y0 == 0.5
    assert ax.patches[2].get_bbox().y1 == 1

def test_make_zone_bands_zorder(mock_figure, test_thresholds):
    """Test that zone bands are drawn behind other plot elements"""
    fig, ax = mock_figure
    ymin, ymax = 0, 5
    make_zone_bands(ax, ymin, ymax, test_thresholds)
    
    # All patches should have zorder=0 to be drawn behind other elements
    for patch in ax.patches:
        assert patch.get_zorder() == 0

def test_make_zone_bands_labels(mock_figure, test_thresholds):
    """Test that zone bands have correct labels"""
    fig, ax = mock_figure
    ymin, ymax = 0, 5
    make_zone_bands(ax, ymin, ymax, test_thresholds)
    
    labels = [patch.get_label() for patch in ax.patches]
    assert labels == ["Distress Zone", "Grey Zone", "Safe Zone"]

def test_add_zone_labels(mock_figure, test_thresholds):
    fig, ax = mock_figure
    ymin, ymax = 0, 5
    add_zone_labels(ax, ymin, ymax, test_thresholds)
    
    # Check that we have 3 text elements (Distress, Grey, Safe)
    assert len(ax.texts) == 3
    
    # Check text content and colors
    assert ax.texts[0].get_text() == "Distress"
    assert ax.texts[1].get_text() == "Grey"
    assert ax.texts[2].get_text() == "Safe"
    
    # Check colors (in RGB format)
    assert ax.texts[0].get_color() == "#a60000"
    assert ax.texts[1].get_color() == "#444444"
    assert ax.texts[2].get_color() == "#007a00"

def test_add_zone_labels_edge_cases(mock_figure):
    fig, ax = mock_figure
    ymin, ymax = -10, 10  # Test with wide range
    thresholds = {"distress_zone": -5, "safe_zone": 5}
    add_zone_labels(ax, ymin, ymax, thresholds)
    
    # Check text properties
    for text in ax.texts:
        assert text.get_ha() == "left"  # horizontal alignment
        assert text.get_va() == "center"  # vertical alignment
        assert text.get_fontsize() == 9
        assert text.get_fontweight() == "bold"
        assert text.get_transform() == ax.transAxes
        assert text.get_zorder() == 1000  # should be above other elements

def test_add_zone_labels_position(mock_figure, test_thresholds):
    """Test that labels are positioned correctly relative to zones"""
    fig, ax = mock_figure
    ymin, ymax = 0, 5
    add_zone_labels(ax, ymin, ymax, test_thresholds)
    
    # Labels should be vertically ordered: Distress < Grey < Safe
    y_positions = [text.get_position()[1] for text in ax.texts]
    assert y_positions == sorted(y_positions)  # vertical positions should be in ascending order
    
    # All labels should be at x=0.02 (2% from left edge)
    x_positions = [text.get_position()[0] for text in ax.texts]
    assert all(x == 0.02 for x in x_positions)

def test_make_legend_elements(test_thresholds):
    safe = float(test_thresholds["safe_zone"])
    distress = float(test_thresholds["distress_zone"])
    elements = make_legend_elements(safe, distress)
    
    # Check that we have 4 elements (3 patches + 1 line)
    assert len(elements) == 4
    
    # Check that the last element is a Line2D object (Z-Score trend line)
    assert isinstance(elements[3], Line2D)
    
    # Check labels
    assert elements[0].get_label() == f"Distress Zone\n≤ {distress}"
    assert elements[1].get_label() == f"Grey Zone\n{distress} to {safe}"
    assert elements[2].get_label() == f"Safe Zone\n≥ {safe}"
    assert elements[3].get_label() == "Z-Score\nTrend Line"

def test_make_legend_elements_basic():
    """Test basic legend element creation"""
    safe, distress = 2.9, 1.23
    elements = make_legend_elements(safe, distress)
    
    # Should have 4 elements: 3 patches for zones + 1 line
    assert len(elements) == 4
    
    # Check patch properties
    patches = [e for e in elements if isinstance(e, Patch)]
    assert len(patches) == 3
    
    # Check line properties
    lines = [e for e in elements if isinstance(e, Line2D)]
    assert len(lines) == 1
    line = lines[0]
    assert line.get_color() == "blue"
    assert line.get_marker() == "s"
    assert line.get_markersize() == 4
    assert line.get_linestyle() == "-"
    assert line.get_linewidth() == 1

def test_make_legend_elements_labels():
    """Test legend element labels"""
    safe, distress = 3.0, 1.5
    elements = make_legend_elements(safe, distress)
    
    labels = [e.get_label() for e in elements]
    expected_labels = [
        "Distress Zone\n≤ 1.5",
        "Grey Zone\n1.5 to 3.0",
        "Safe Zone\n≥ 3.0",
        "Z-Score\nTrend Line"
    ]
    assert labels == expected_labels

def test_make_legend_elements_colors():
    """Test legend element colors and styles"""
    safe, distress = 2.9, 1.23
    elements = make_legend_elements(safe, distress)
    
    # Check patch colors and alpha values
    patches = [e for e in elements if isinstance(e, Patch)]
    assert patches[0].get_facecolor() == (1, 0.4, 0.4, 0.8)  # Red with alpha
    assert patches[1].get_facecolor() == (0.8, 0.8, 0.8, 0.6)  # Grey with alpha
    assert patches[2].get_facecolor() == (0.4, 1, 0.4, 0.5)  # Green with alpha

def test_save_plot_with_legend(mock_figure, test_thresholds, tmp_path):
    fig, ax = mock_figure
    safe = float(test_thresholds["safe_zone"])
    distress = float(test_thresholds["distress_zone"])
    elements = make_legend_elements(safe, distress)
    out_path = tmp_path / "test_plot.png"
    
    # Draw something simple
    ax.plot([1, 2, 3], [1, 2, 3])
    
    save_plot_with_legend(fig, elements, str(out_path))
    
    # Check that the file was created
    assert out_path.exists()
    # Check file size is non-zero
    assert out_path.stat().st_size > 0

def test_make_zone_bands_safe_equals_distress(mock_figure):
    fig, ax = mock_figure
    ymin, ymax = 0, 5
    thresholds = {"distress_zone": 2.0, "safe_zone": 2.0}
    make_zone_bands(ax, ymin, ymax, thresholds)
    # Should still create 3 bands, but grey zone will have zero height
    assert len(ax.patches) == 3
    assert ax.patches[1].get_bbox().y0 == 2.0
    assert ax.patches[1].get_bbox().y1 == 2.0

def test_make_zone_bands_missing_keys(mock_figure):
    fig, ax = mock_figure
    ymin, ymax = 0, 5
    thresholds = {"safe_zone": 2.0}  # distress_zone missing
    with pytest.raises(KeyError):
        make_zone_bands(ax, ymin, ymax, thresholds)

def test_add_zone_labels_missing_keys(mock_figure):
    fig, ax = mock_figure
    ymin, ymax = 0, 5
    thresholds = {"distress_zone": 1.0}  # safe_zone missing
    with pytest.raises(KeyError):
        add_zone_labels(ax, ymin, ymax, thresholds)
