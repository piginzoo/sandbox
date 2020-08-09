import queue
import logging
import numpy as np
from shapely.geometry import *

logger = logging.getLogger(__name__)


class Row:
    def __init__(self):
        self.columns = []

    def add(self, column):
        self.columns.append(column)

    def find_column(self, header_column):
        for col in self.columns:
            if col.header_column == header_column:
                return col
        return None

    def __str__(self):
        return "\t|\t".join([str(c) for c in self.columns])

    def __repr__(self):
        return self.__str__()


class Column:
    def __init__(self, header_column, bbox=None):
        if bbox:
            self.bboxes = [bbox]
        else:
            self.bboxes = []
        self.header_column = header_column

    def add(self, bbox):
        self.bboxes.append(bbox)

    def __str__(self):
        return "".join([str(bbox) for bbox in self.bboxes])

    def __repr__(self):
        return self.__str__()


class HeaderColumn:
    def __init__(self, header_bbox, left, right, top, bottom):
        self.header_bbox = header_bbox
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.pos = np.array([[left, top], [right, top], [right, bottom], [left, bottom]])

    def __str__(self):
        return str(self.header_bbox)

    def __repr__(self):
        return str(self.header_bbox)

    def __eq__(self, other):
        return self.header_bbox == other.header_bbox


class Table:
    """
    [] 我怎么知道我是表的一行，
    """

    def __init__(self, header_bboxes, image_width, image_heigth):
        self.header_bboxes = header_bboxes
        self.header_columns = self.create_header_columns(header_bboxes, image_width, image_heigth)
        self.rows = []

    def __str__(self):
        return "\n".join([str(row) for row in self.rows])

    def __repr__(self):
        return self.__str__()

    def is_end(self, row_bboxes):
        import bbox
        if len(row_bboxes) > 0:
            field = bbox.find_similar_key(row_bboxes[0].txt, "table_end")
            if field:
                logger.debug("表识别：此表格已结束，遇到结束行：%r", row_bboxes)
                return True
        return False

    def build(self, all_row_boxes, bbox_averate_height):

        self.stack = queue.LifoQueue()

        # 逐行处理
        row_detect_counter = 0
        for i in range(len(all_row_boxes) - 1):
            row_bboxes = all_row_boxes[i]

            # 最多探测3行
            if row_detect_counter > 3:
                logger.debug("表识别：行探测：已经向下探测了3行，都不是表格行，认为表格结束！")
                break;

            if self.is_end(row_bboxes):
                logger.debug("表识别：出现了结束行[%r]，认为表格结束了！", row_bboxes)
                break;

            # 解析这一行bboxes，看看是不是可以形成一个行Row
            new_row = self.parse_row(row_bboxes)
            # 如果这行是一行表数据，那么计数器重置，回过头出去之前积累的行数
            if new_row:
                current_row = new_row
                row_detect_counter = 0  # 确认是新行后，探测一行的计数器重置
                logger.debug("表识别：行识别：识别新行的后处理，把堆积的%d行表数据回填到表里", self.stack.qsize())
                while not self.stack.empty():  # 把之前积累的行，都消化掉
                    old_row_bboxes = self.stack.get()
                    self.find_matched_bbox_for_header_column(current_row, old_row_bboxes)
                    logger.debug("表识别：行识别：把堆积行bboxes数据[%r]回填到表里", old_row_bboxes)
            # 如果这行不是表行数据
            else:
                logger.debug("表识别：当前行[%r]已经不是表格行了，暂时尝试放入stack", row_bboxes)
                self.stack.put(row_bboxes)
                row_detect_counter += 1

            # TODO: 这个下一步再考虑
            # is_qualtified_next_row = self.parse_row(next_row_bboxes)
            # two_row_bboxes_distance = row_parser.calculate_2_row_bboxes_distance(is_qualtified_row,is_qualtified_next_row)
            # if two_row_bboxes_distance>2*bbox_averate_height:
            #     logger.debug("表识别：两行【%r】和【%r】行间距，超过了2倍的bbox平均高度", row_bboxes,next_row_bboxes,)
            #     break;

    def create_header_columns(self, header_bboxes, image_width, image_heigth):
        header_columns = []
        # 对于一行bboxes们，先排个序
        header_bboxes = sorted(header_bboxes, key=lambda _bbox: _bbox.pos[:, 0].min())
        for i in range(len(header_bboxes)):
            top = header_bboxes[i].top()

            if i == 0:
                left = 0
            else:
                left = int((header_bboxes[i].left() + header_bboxes[i - 1].right()) / 2)
            if i == len(header_bboxes) - 1:
                right = image_width
            else:
                right = int((header_bboxes[i + 1].left() + header_bboxes[i].right()) / 2)
            logger.debug("表识别：表头识别：拆分表头[左:%f],[右:%f],[上:%f],[下:%f]", left, right, top, image_heigth)
            _header_column = HeaderColumn(header_bboxes[i], left, right, top, image_heigth)
            header_columns.append(_header_column)
        logger.debug("表识别：表头识别：识别了表的表头[%d]列", len(header_columns))
        return header_columns

    # 来！我们来分析一个框是不是属于这个表格，属于那个列
    # 观察2-3行，如果都不是，就认为表格结束了
    def parse_row(self, row_bboxes):
        logger.debug("表识别：行识别：开始识别这一行%r/%r", row_bboxes, self.header_columns)

        # 如何判断是不是一行，应该是凡是匹配度超过1半，
        # 那啥叫匹配度
        row = Row()
        matched_bbox_counter = self.find_matched_bbox_for_header_column(row, row_bboxes)

        # TODO 这个rule很重要:
        #   如果匹配的框数量大于1个，2+；并且，比例大于，
        if matched_bbox_counter > 1 and (matched_bbox_counter / len(self.header_columns)) > 0.4:
            logger.debug("此行是表的数据行：%r", row)
            self.rows.append(row)
            return row
        return None

    def find_matched_bbox_for_header_column(self, row, row_bboxes):
        matched_bbox_counter = 0
        for header_column in self.header_columns:
            column = row.find_column(header_column)
            if not column:
                column = Column(header_column)
                row.add(column)
                logger.debug("行识别：无法在行内找到标题列[%r]，创建之", header_column)
            else:
                logger.debug("行识别：在行内找到标题列[%r]，复用它", header_column)
            for bbox in row_bboxes:
                if self.is_bbox_match_column(header_column, bbox):
                    matched_bbox_counter += 1
                    logger.debug("此bbox[%r]属于列[%r]，把此bbox加入到这列", bbox, header_column)
                    column.add(bbox)
            logger.debug("加入一列：%s", str(column))

        return matched_bbox_counter

    def is_bbox_match_column(self, header_column, bbox):
        bbox_poly = Polygon(bbox.pos)
        header_column_poly = Polygon(header_column.pos)
        intersection_area = header_column_poly.intersection(bbox_poly).area
        bbox_area = bbox_poly.area
        ratio = intersection_area / bbox_area
        if ratio > 0.5:
            logger.debug("表识别：行识别：列识别：!这个bbox[%r]和列[%r]相交比超过0.5[%.2f]，我认定你属于这列", bbox, header_column, ratio)
            return True
        logger.debug("表识别：行识别：列识别：这个bbox[%r]和列[%r]相交比小于0.5[%.2f]，我认定你不属于这列", bbox, header_column, ratio)
        return False


# 构建表格，假设表格是标题一下的
def table_builder(header_bboxes, left_row_bboxes, average_bbox_height, image_width, image_heigth):
    logger.debug("表分析:开始做表分析，标题行:%r，剩余需要分析的行：%d行", header_bboxes, len(left_row_bboxes))

    # 计算每个框的的距离
    table = Table(header_bboxes, image_width, image_heigth)
    table.build(left_row_bboxes, average_bbox_height)
    return table