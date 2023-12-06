#pragma once

#include <string>
#include <vector>

using matrix_t = std::vector<std::vector<int>>;

matrix_t read_matrix(const std::string& input_filename, const char separator = '\t');
void print_matrix(const matrix_t& matrix);

