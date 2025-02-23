def extract_tour_section(filename):
    with open(filename, 'r') as file:
        # 读取所有行
        lines = file.readlines()

        # 找到 TOUR_SECTION 部分
        start_index = None
        dimension = None
        tour_section = []

        for line in lines:
            # 查找 DIMENSION 行，获取维度
            if line.startswith("DIMENSION"):
                dimension = int(line.split(":")[1].strip())

            # 查找 TOUR_SECTION 开始
            if line.startswith("TOUR_SECTION"):
                start_index = lines.index(line) + 1  # TOUR_SECTION 后一行才是数字开始

            # 一旦找到 TOUR_SECTION 后面部分，开始处理
            if start_index and start_index < len(lines):
                tour_section_data = lines[start_index:]
                break

        # 过滤数字部分，去除 DIMENSION 数量的数字，并去掉 -1
        for num in tour_section_data:
            num = num.strip()
            if num == "-1":
                break

            if int(num) == dimension:
                continue
            if len(tour_section) < dimension:
                tour_section.append(int(num))

        return tour_section


# 使用示例
filename = "test.tour"
result = extract_tour_section(filename)
print(result)

