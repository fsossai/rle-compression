#pragma once

#include "dataframe.h"
#include "path.h"

Path nearest_neighbor(DataFrame& dataframe, int start_node=0);
Path multi_list(DataFrame& dataframe, matrix_t& L);
void sample_3edges(int &i, int &j, int &k, int nnodes);
bool refine_2opt(Path& path, int time_limit);
bool refine_2opt_exhaustive(Path& path, int time_limit);
bool refine_3opt(Path& path, DataFrame& dataframe, int time_limit);
bool refine_4opt(Path& path, int time_limit);
void diversificate(Path& path, int nkicks);
void vns(Path& path, int time_limit=60'000);

