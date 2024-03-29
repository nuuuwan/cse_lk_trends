import os

from utils import Log, _

from cse_lk_trends.DataCSEASPI import DataCSEASPI

DIR_CHARTS = 'charts'

log = Log('BoxPlot')


class Style:
    WIDTH = 1200
    HEIGHT = int(WIDTH * 9 / 16)

    SPAN = 0.02

    MIN_VAL = -0.24
    MAX_VAL = 0.25
    N_GROUPS = int((MAX_VAL - MIN_VAL) / SPAN) + 1
    DIM_X = int(WIDTH / (N_GROUPS + 3))
    DIM_Y = DIM_X * 0.25
    N_GROUPS_Y = 61

    class COLOR:
        BACKGROUND = '#f8f8f8'

    class FONT:
        # FAMILY = 'P22 Johnston Underground'
        FAMILY = 'monospace'
        SIZE = 12


class BoxPlot:
    def __init__(self, data_list: list[DataCSEASPI]):
        self.data_list = data_list

    @property
    def group_to_data_list(self):
        group_to_data_list = {}
        for data in self.data_list:
            group = int((data.change_plot - Style.MIN_VAL) / Style.SPAN)
            if group not in group_to_data_list:
                group_to_data_list[group] = []
            group_to_data_list[group].append(data)

        return group_to_data_list

    @staticmethod
    def box(i: int, j: int, data: DataCSEASPI):
        x = Style.DIM_X * (i + 1)
        y = Style.DIM_Y * (Style.N_GROUPS_Y - j)
        width = Style.DIM_X
        height = Style.DIM_Y

        fill = BoxPlot.get_val_color(data.change_plot)
        return _(
            'g',
            [
                _(
                    'rect',
                    None,
                    dict(
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        fill=fill,
                        stroke=None,
                    ),
                ),
                _(
                    'text',
                    data.date_str,
                    dict(
                        x=x + width / 2,
                        y=y + height * 0.75,
                        fill='#000',
                        text_anchor="middle",
                        font_family=Style.FONT.FAMILY,
                        font_size=Style.FONT.SIZE * 0.8,
                    ),
                ),
            ],
        )

    @staticmethod
    def background():
        return _(
            'rect',
            None,
            dict(
                x=0,
                y=0,
                width=Style.WIDTH,
                height=Style.HEIGHT,
                fill=Style.COLOR.BACKGROUND,
            ),
        )

    @staticmethod
    def get_val_color(val: float):
        p = (val - Style.MIN_VAL) / (Style.MAX_VAL - Style.MIN_VAL)
        h = 150 * p
        color = f'hsl({h},100%,40%)'
        return color

    @staticmethod
    def x_axis_label(i: int):
        x = Style.DIM_X * (i + 1)
        y = Style.DIM_Y * (Style.N_GROUPS_Y + 2.5)
        val = Style.MIN_VAL + i * Style.SPAN
        val_str = f'{val:.0%}'
        if val > Style.SPAN / 2:
            val_str = '+' + val_str

        fill = BoxPlot.get_val_color(val)

        return _(
            'text',
            val_str,
            dict(
                x=x,
                y=y,
                fill=fill,
                text_anchor="middle",
                font_family=Style.FONT.FAMILY,
                font_size=Style.FONT.SIZE,
            ),
        )

    @staticmethod
    def title():
        return _(
            'g',
            [
                _(
                    'text',
                    'Colombo Stock Exchange (CSE) - All Share Index (ASPI)',
                    dict(
                        x=Style.WIDTH / 2,
                        y=Style.DIM_Y * 3,
                        fill="#000",
                        text_anchor="middle",
                        font_family=Style.FONT.FAMILY,
                        font_size=Style.FONT.SIZE * 2,
                    ),
                ),
                _(
                    'text',
                    'Performance by Month',
                    dict(
                        x=Style.WIDTH / 2,
                        y=Style.DIM_Y * 3 + Style.FONT.SIZE * 2,
                        fill="#000",
                        text_anchor="middle",
                        font_family=Style.FONT.FAMILY,
                        font_size=Style.FONT.SIZE * 1.4,
                    ),
                ),
            ],
        )

    @property
    def svg(self):
        group_to_data_list = self.group_to_data_list

        box_list = []
        for i in range(Style.N_GROUPS + 2):
            data_list = group_to_data_list.get(i, [])
            for j, data in enumerate(data_list):
                box = BoxPlot.box(i, j, data)
                box_list.append(box)

            box_list.append(BoxPlot.x_axis_label(i))

        return _(
            'svg',
            [BoxPlot.background()] + box_list + [BoxPlot.title()],
            dict(width=Style.WIDTH, height=Style.HEIGHT),
        )

    def write(self, svg_path: str):
        self.svg.store(svg_path)
        log.info(f'Wrote chart to {svg_path}')
        os.startfile(svg_path)


if __name__ == '__main__':
    data_list = DataCSEASPI.list_all_aggr(lambda d: d.month)
    BoxPlot(data_list).write(os.path.join(DIR_CHARTS, 'box_plot.svg'))
