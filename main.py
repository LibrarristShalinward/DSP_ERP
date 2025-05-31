from backend.plan.scale import ScalePlan
from dsp import *
from frontend.proline import ProdectionLineWindow
import ctypes
import dearpygui.dearpygui as dpg

ctypes.windll.shcore.SetProcessDpiAwareness(2)

# 创建上下文和主题
dpg.create_context()

# region 产线规划
tar = {}
sp = ScalePlan(tar)
item_scale, rcp_scale = sp.scales
used_items, used_rcps = set(item_scale.keys()), set(rcp_scale.keys())
# endregion

font_path = r"C:\Users\LibrarristShalinward\AppData\Local\Microsoft\Windows\Fonts\MapleMono-NF-CN-Regular.ttf"

# 加载字体（需要确保路径有效）
with dpg.font_registry():
    # 参数说明：字体文件路径，字体大小，自定义字体名称
    with dpg.font(font_path, 30, tag = "MapleMono") as custom_font: 
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)

# 新增的窗口背景主题
with dpg.theme() as window_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255, 255, 255, 0))

# 创建主窗口
pro_window = ProdectionLineWindow(
    used_items, 
    used_rcps
)
dpg.set_viewport_resize_callback(pro_window.update_fig_position)

# 应用自定义主题到按钮
dpg.bind_item_theme(pro_window.tag, window_theme)
dpg.bind_item_font(pro_window.tag, custom_font)

# 视口设置
dpg.create_viewport(
    title = "Centered Button Example",
    width = 900,
    height = 600
)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(pro_window.tag, True)









# 主循环
while True:
    dpg.render_dearpygui_frame()
dpg.cleanup_dearpygui()
dpg.destroy_context()