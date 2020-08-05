import logging
import numpy as np
from shapely.geometry import *
import row_parser

logger = logging.getLogger(__name__)


class Row:
    def __init__(self):
        self.columns = []

    def add(self, column):
        self.columns.append(column)

    def __str__(self):
        return "|".join(self.columns)

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
        return "".join(self.bboxes)

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


class Table:
    """
    [] 我怎么知道我是表的一行，
    """

    def __init__(self, header_bboxes, image_width, image_heigth):
        self.header_bboxes = header_bboxes
        self.header_columns = self.create_header_columns(header_bboxes, image_width, image_heigth)
        self.rows=[]


    def __str__(self):
        return "\n".join(self.rows)

    def __repr__(self):
        return self.__str__()


    def is_end(self,row_bboxes):
        import bbox
        if len(row_bboxes)>0:
            field = bbox.find_similar_key(row_bboxes[0].txt,"table_end")
            if field:
                logger.debug("表识别：此表格已结束，遇到结束行：%r",row_bboxes)
                return True
        return False


    def build(self,all_row_boxes,bbox_averate_height):
        for i in range(len(all_row_boxes)-1):
            row_bboxes = all_row_boxes[i]
            next_row_bboxes = all_row_boxes[i+1]
            if self.is_end(row_bboxes):
                logger.debug("表识别：识别结束了，出现了结束行[%r]", row_bboxes)
                break;
            is_qualtified_row = self.parse_row(row_bboxes)
            if not is_qualtified_row:
                logger.debug("表识别：当前行[%r]已经不是表格行了，识别结束", row_bboxes)
                break;

            # TODO: 这个下一步再考虑
            # is_qualtified_next_row = self.parse_row(next_row_bboxes)
            # two_row_bboxes_distance = row_parser.calculate_2_row_bboxes_distance(is_qualtified_row,is_qualtified_next_row)
            # if two_row_bboxes_distance>2*bbox_averate_height:
            #     logger.debug("表识别：两行【%r】和【%r】行间距，超过了2倍的bbox平均高度", row_bboxes,next_row_bboxes,)
            #     break;

    def create_header_columns(self, header_bboxes, image_width, image_heigth):
        header_columns = []
        for i in range(len(header_bboxes)):
            top = header_bboxes[i].top()

            if i == 0:
                left = 0
            else:
                left = int((header_bboxes[i].left() - header_bboxes[i - 1].right()) / 2)

            if i == len(header_bboxes) - 1:
                right = image_width
            else:
                right = int((header_bboxes[i + 1].left() - header_bboxes[i].right()) / 2)

            _header_column = HeaderColumn(header_bboxes, left, right, top, image_heigth)
            header_columns.append(_header_column)
        logger.debug("表识别：表头识别：识别了表的表头[%d]列",len(header_columns))
        return header_columns



    # 来！我们来分析一个框是不是属于这个表格，属于那个列
    # 观察2-3行，如果都不是，就认为表格结束了
    def parse_row(self, row_bboxes):

        # 如何判断是不是一行，应该是凡是匹配度超过1半，
        # 那啥叫匹配度
        matched_bbox_counter = 0
        for bbox in row_bboxes:
            row = Row()
            header_column = self.find_match_column(bbox)
            if header_column:
                matched_bbox_counter += 1
                row.add(Column(header_column,bbox))

        # TODO 这个rule很重要:
        #   如果匹配的框数量大于1个，2+；并且，比例大于，
        if matched_bbox_counter > 1 and (matched_bbox_counter / len(self.header_columns)) > 0.4:
            self.rows.append(row)
            return True
        return False

    def find_match_column(self, bbox):
        bbox_poly = Polygon(bbox.pos)
        for header_column in self.header_columns:
            header_column_poly = Polygon(header_column.pos)
            intersection_area = header_column_poly.intersection(bbox_poly).area
            bbox_area = bbox_poly.area
            ratio = intersection_area / bbox_area
            if ratio > 0.5:
                logger.debug("表识别：行识别：列识别：!这个bbox[%r]和列[%r]相交比超过0.5[%.2f]，我认定你属于这列", bbox, header_column, ratio)
                return header_column
        logger.debug("表识别：行识别：列识别：这个bbox[%r]和列[%r]相交比小于0.5[%.2f]，我认定你不属于这列", bbox, header_column, ratio)
        return None


# 构建表格，假设表格是标题一下的
def table_builder(header_bboxes, left_row_bboxes,average_bbox_height,image_width, image_heigth):
    logger.debug("表分析:开始做表分析，标题行:%r，剩余需要分析的行：%d行", header_bboxes, len(left_row_bboxes))

    # 计算每个框的的距离
    table = Table(header_bboxes,image_width, image_heigth)
    table.build(left_row_bboxes,average_bbox_height)
    return table
