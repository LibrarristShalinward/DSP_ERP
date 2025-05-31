from .utils import func2getitem, method2geitem
from functools import cached_property
from pathlib import Path
import yaml



class LayoutConfig: 
    """
    布局配置类，用于读取布局配置文件并存储相关参数。
    """
    def __init__(self, file_path): 
        # region 基本属性
        with open(file_path, 'r', encoding = 'utf-8') as file:
            yml = yaml.safe_load(file)
        self.icon_size: float = yml['icon']['size']
        """图标大小"""
        self.iborder: float = yml['icon']['border']
        """第一行/最后一行图标与海报边界的间距"""
        self.cgap: float = yml['connection']['gap']
        """连接线间距"""
        self.cgap2icon: float = yml['connection']['gap2icon']
        """连接线与图标的额外间距(连接线与图标间距等于该值+gap/2)"""
        self.cgap2border: float = yml['connection']['gap2border']
        """连接线与海报边界的额外间距(连接线与海报边界间距等于该值+gap/2)"""
        # endregion

        # region 计算属性: 连接线节点坐标相关变量
        self.con_cl0_pos0 = self.cgap2border + self.cgap / 2.
        """第一列图标左边的簇中第一条的x坐标/第一行图标下方的簇中第一条的y坐标"""
        self.con_pos0 = self.cgap2icon + (self.icon_size + self.cgap) / 2.
        """图标右侧纵向连接线簇最左边一条与其中心距离"""
        # endregion
cfg = LayoutConfig(
    Path(__file__).parent / 'config.yaml'
)



class _Layout:
    """
    _Layout类是Layout类的计算部分
    """
    def __init__(self, 
                icon_row: int, 
                icon_col: int,
                inner_con_cap: tuple[int, int], 
                outer_con_cap: tuple[int, int, int], 
                cfg: LayoutConfig = cfg
            ): 
        """
        Layout类用于计算图标和连接线的位置。

        Parameters:
            icon_num (int): 图标行数
            icon_col (int): 图标列数
            inner_con_cap (tuple[int, int]):
                - 左右相邻图标之间的连接线数量
                - 上下相邻图标之间的连接线数量/最后一列下方连接线数量
            outer_con_cap (tuple[int, int]):
                - 最左一列图标与左边界之间的连接线数量
                - 最右一列图标与右边界之间的连接线数量
                - 第一行图标与上边界之间的连接线数量
            cfg (LayoutConfig): 布局配置类，默认为cfg
        """
        # region 基本属性
        self.nrow = icon_row
        """图标行数"""
        self.ncol = icon_col
        """图标列数"""
        self.cfg = cfg
        """布局配置类"""
        self.inner_con_cap = inner_con_cap
        """左右和上下相邻图标之间的连接线数量"""
        self.outer_con_cap = outer_con_cap
        """图标与左右边界之间的连接线数量"""
        # endregion

        # region 计算属性: 间距
        self.icon_gap = (
            self.inner_con_cap[0] * self.cfg.cgap + 2 * self.cfg.cgap2icon, 
            self.inner_con_cap[1] * self.cfg.cgap + 2 * self.cfg.cgap2icon
        )
        """图标(左右, 上下)间距"""

        # endregion

        # region 计算属性: 图标坐标
        self.icon_pos0 = (
            self.cfg.cgap2border + self.cfg.cgap * self.outer_con_cap[0] + self.cfg.cgap2icon + self.cfg.icon_size / 2., 
            self.cfg.cgap2border + self.cfg.cgap * self.outer_con_cap[2] + self.cfg.cgap2icon + self.cfg.icon_size / 2.
        )
        """左上角图标中心点坐标"""
        self.icon_step = (
            self.icon_gap[0] + self.cfg.icon_size, 
            self.icon_gap[1] + self.cfg.icon_size
        )
        """相邻图标中心点间距"""
        # endregion



class Layout(_Layout): 
    """
    Layout类用于计算图标和连接线的位置。
    图标阵列外，只有左右有连接线，上方无连接线。
    后续坐标以图片左上角为零点，向右和向上为正方向。
    """
    @cached_property
    def fig_size(self): 
        """图像大小"""
        return (
            (
                self.cfg.cgap2icon * 2 + 
                self.cfg.icon_size + 
                self.cfg.cgap * self.inner_con_cap[0]
            ) * self.ncol + 
            self.cfg.cgap2border * 2 + 
            self.cfg.cgap * sum(self.outer_con_cap), 
            (
                self.cfg.cgap2icon * 2 + 
                self.cfg.icon_size + 
                self.cfg.cgap * self.inner_con_cap[1]
            ) * self.nrow + 
            self.cfg.cgap2border * 2 + 
            self.cfg.cgap * self.outer_con_cap[2]
        )

    # region 可索引属性：坐标
    @property
    @method2geitem
    def icon_pos(self, idx: tuple[int, int]) -> tuple[float, float]:
        """
        获取图标中心点坐标

        Parameters:
            idx tuple[int, int]: 图标索引(行号, 列号)

        Returns:
            tuple[float, float]: 图标中心点坐标
        """
        row, col = idx
        # 无效索引
        if row >= self.nrow or row < 0: 
            raise IndexError(f"Row index {row} out of range (0-{self.nrow})")
        if col >= self.ncol or col < 0:
            raise IndexError(f"Column index {col} out of range (0-{self.ncol})")
        # 计算坐标
        return (
            self.icon_pos0[0] + col * self.icon_step[0], 
            self.icon_pos0[1] + row * self.icon_step[1]
        )
    
    @property
    @method2geitem
    def _clust_pos_x0(self, idx: int) -> float:
        """
        获取纵向连接线簇中最左一条的x坐标

        Parameters:
            idx (int): 最左一列图标与左边界之间的连接线为第-1簇，第一列图标右侧的连接线为第0簇……最右一列图标与右边界之间的连接线为第ncol - 1簇，再向右的一簇为ncol簇。
        Returns:
            float: 簇中最左一条的x坐标
        """
        if idx == -1: #第一列图标左边的簇
            return self.cfg.con_cl0_pos0
        elif idx >= 0 and idx < self.ncol: # 两列图标之间的簇及最右边一列图标右边的簇
            return self.icon_pos[0, idx][0] + self.cfg.con_pos0
        elif idx == self.ncol: 
            return self._clust_pos_x0[self.ncol - 1] + self.cfg.cgap * self.inner_con_cap[0]
        else: # 无效索引
            raise IndexError(f"Column index {idx} out of range (-1-{self.ncol})")
    
    @property
    @method2geitem
    def con_pos_x(self, idx: int) -> func2getitem[int, float]:
        """
        获取连接线纵向部分x坐标

        Parameters:
            idx (int): 同_clust_pos_x
        Returns:
            float: 能返回对应簇内所有x坐标的可索引对象
        """
        x0 = self._clust_pos_x0[idx] # 簇中最左一条的x坐标+cl_idx合法性检查
        if idx == -1:
            n_con = self.outer_con_cap[0] # 第一列图标左边的簇
        elif idx >= 0 and idx < self.ncol: 
            n_con = self.inner_con_cap[0]
        else: # 最右边一列图标右边的簇
            n_con = self.outer_con_cap[1]
        @func2getitem
        def wrapper(idx: int) -> float: 
            """
            获取连接线纵向部分x坐标

            Parameters:
                idx (int): 每一簇最左边为第0条，该索引可以类似list的索引取包括负值的任何整数值，-1表示最后一条连接线，依此类推。
            Returns:
                float: 连接线x坐标
            """
            return x0 + (idx % n_con) * self.cfg.cgap
        return wrapper
    
    @property
    @method2geitem
    def con_pos_y(self, idx: int) -> func2getitem[int, float]: 
        """
        获取连接线横向部分y坐标

        Parameters:
            idx (int): 第几簇连接线。第一行图标下方的连接线为第0簇……最后一行图标下方为第nrow-1簇。
        Returns:
            float: 能返回对应簇内所有y坐标的可索引对象
        """
        # 合法性检查
        if idx == -1: # 第一行图标下方的连接线为第0簇
            y0 = self.cfg.con_cl0_pos0
            cap = self.outer_con_cap[2]
        elif idx >= 0 and idx < self.nrow: # 最后一行图标下方的连接线为第nrow-1簇
            y0 = self.icon_pos[idx, 0][1] + self.cfg.con_pos0
            cap = self.inner_con_cap[1]
        else: 
            raise IndexError(f"Row index {idx} out of range (-1-{self.nrow - 1})")
        
        @func2getitem
        def wrapper(idx: int) -> float: 
            """
            获取连接线纵向部分y坐标

            Parameters:
                idx (int): 每一簇最上方为第0条，该索引可以类似list的索引取包括负值的任何整数值，-1表示最后一条连接线，依此类推。
            Returns:
                float: 连接线y坐标
            """
            return y0 + (idx % cap) * self.cfg.cgap
        return wrapper
    
    @property
    @method2geitem
    def _con_icon_node(self, idx: tuple[int, int]) -> float:
        """
        获取连接线从图标上方或下方引出时相对图标中心的x坐标

        Parameters:
            idx (int): (要获取第几条线的坐标, 将引出几条线)
        Returns:
            float: 连接线从图标上方或下方引出时相对图标中心的x坐标
        """
        return self.cfg.cgap * (idx[0] + (idx[1] - 1) / 2.)
    
    @property
    @method2geitem
    def con_start(self, icon_idx: tuple[int, int]) -> func2getitem[tuple[int, int], tuple[float, float]]: 
        """
        获取连接线从图标引出点的坐标

        Parameters:
            icon_idx (tuple[int, int]): 同icon_pos索引
        Returns:
            func2getitem[tuple[int, int], tuple[float, float]]: 一个可索引具体坐标的对象
        """
        x0, y0 = self.icon_pos[icon_idx] # 图标中心坐标
        y0 -= self.cfg.icon_size / 2. # 图标下方引出连接线时，y坐标要减去图标半径
        @func2getitem
        def wrapper(idx: tuple[int, int]) -> tuple[float, float]: 
            """
            获取连接线从图标引出点的坐标

            Parameters:
                idx (tuple[int, int]): 同_con_icon_node索引
            Returns:
                tuple[float, float]: 连接线从图标引出点的坐标
            """
            return x0 + self._con_icon_node[idx], y0
        return wrapper

    @property
    @method2geitem
    def con_end(self, icon_idx: tuple[int, int]) -> func2getitem[tuple[int, int], tuple[float, float]]: 
        """
        获取连接线到达图标点的坐标

        Parameters:
            icon_idx (tuple[int, int]): 同icon_pos索引
        Returns:
            func2getitem[tuple[int, int], tuple[float, float]]: 一个可索引具体坐标的对象
        """
        x0, y0 = self.icon_pos[icon_idx] # 图标中心坐标
        y0 += self.cfg.icon_size / 2. # 图标上方引出连接线时，y坐标要加上图标半径
        @func2getitem
        def wrapper(idx: tuple[int, int]) -> tuple[float, float]: 
            """
            获取连接线到达图标点的坐标

            Parameters:
                idx (tuple[int, int]): 同_con_icon_node索引
            Returns:
                tuple[float, float]: 连接线从图标引出点的坐标
            """
            return x0 + self._con_icon_node[idx], y0
        return wrapper
    
    @property
    @method2geitem
    def canvas(self, vertices: tuple[int, int, int, int]) -> tuple[float, float, float, float]: 
        """根据icon索引确定一个画布范围

        Args:
            vertices (tuple[int, int, int, int]): icon索引(上，下, 左, 右)

        Returns:
            tuple[float, float, float, float]: 画布范围(左, 右，下，上)
        """
        gap = self.cfg.icon_size / 2.
        t, b, l, r = vertices
        return (
            self.icon_pos[0, l][0] + gap,
            self.icon_pos[0, r][0] + gap,
            self.icon_pos[b, 0][1] + gap,
            self.icon_pos[t, 0][1] + gap
        )
    # endregion