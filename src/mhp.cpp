#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <algorithm>
#include <limits>
#include <unordered_map>
#include <list>
#include <chrono>

#include "mhp.h"
#include "LTimer.h"

using namespace std;
using namespace std::chrono;

void swap(vector<int>& v, size_t i, size_t j) {
  auto tmp = v[i];
  v[i] = v[j];
  v[j] = tmp;
}

Path nearest_neighbor(DataFrame& dataframe, int start_node) {
  auto nnodes = dataframe.size();
  auto timer = LTimer(200); // ms
  
  // 'available' lists all node that have not been inserted yet
  printf("Nearest neighbor: initialization ... ");
  fflush(stdout);
  vector<int> available(nnodes);
  for (size_t i = 0; i < nnodes; i++) {
    available[i] = i;
  }
  cout << "done" << endl;

  // path[0] --> path[1] --> ... --> path[nnodes] will be the final path
  Path path(dataframe);
  //
  // Selecting randomly the first node of the path
  path.add(start_node);
  swap(available, start_node, nnodes-1);

  int min_cost;
  int current_cost;

  // Creating the path.
  // From now on, 'nodes-i' can be seen as the number of remaining
  // nodes to selected.

  auto update = [&](int i) {
    printf("\rNearest neighbor: building path %i/%zu (%.1f%%) elapsed=%.1f s",
        i+1, nnodes, 100.f*(i+1)/nnodes, timer.total()/1000.f);
    fflush(stdout);
  };
  update(0);

  int k = 0; // print skip tracker
  //print_skip = 1;
  for (int i = 1, current, nearest; i < nnodes; i++) {
    current = path[i-1];
    min_cost = numeric_limits<int>::max();
    // Finding the nearest point to 'current'
    for (int j = 0; j < nnodes-i; j++, k++) {
      current_cost = dataframe.distance(current, available[j]);
      if (current_cost < min_cost) {
        min_cost = current_cost;
        nearest = j;
      }
    }

    if (timer.uplap()) {
      update(i);
    }

    path.add(available[nearest]);
    swap(available, nearest, nnodes-i-1);
  }
  update(nnodes-1);
  printf("\n");

  return path;
}

Path multi_list(DataFrame& dataframe, matrix_t& L) {
  auto path = Path(dataframe);
  const auto M = L.size();
  const auto nnodes = L[0].size();

  int n = L[0][0];

  path.add(n);

  auto candidate_idx = vector<int>();
  auto prev_idx = vector<int>(M);
  auto prev_it = vector<vector<int>::const_iterator>(M);
  
  auto timer = LTimer(200); // [ms]

  const auto N = L[0].size();
  auto check = vector<int>(N);
  for (int i = 0; i < N; i++) {
    check[i] = i;
  }

  auto description = "building path";
  printf("Multi list: %s 1/%zu (%.1f%%)", 
      description, nnodes, 100.f*1/nnodes);

  while (L[0].size() > 1) {
    candidate_idx.clear();
    for (int i = 0; i < M; i++) {
      const auto N = L[i].size();
      const auto& list = L[i];
      auto it = list.begin();
      auto found = false;
      if (list[0] == n) {
        prev_idx[i] = 0;
        candidate_idx.push_back(list[1]);
        found = true;
      } else {
        for (int j = 1; j < N-1; j++) {
          it++;
          if (list[j] == n) {
            prev_idx[i] = j;
            candidate_idx.push_back(list[j-1]);
            candidate_idx.push_back(list[j+1]);
            found = true;
            break;
          }
        }
      }
      if (!found) {
        it++;
        prev_idx[i] = N-1;
        candidate_idx.push_back(list[N-2]);
        found = true;
      } 
      prev_it[i] = it;
    }

    int min_d = numeric_limits<int>::max();
    int min_i = -1;
    for (auto i : candidate_idx) {
      int d = dataframe.distance(n, i);
      if (d < min_d) {
        min_d = d;
        min_i = i;
      }
    }

    for (int i = 0; i < M; i++) {
      L[i].erase(prev_it[i]);
    }

    path.add(min_i);
    n = min_i;

    if (timer.uplap()) {
      const auto n = path.size();
      printf("\rMulti list: %s %zu/%zu (%.1f%%) elapsed=%.1f s",
          description, n, nnodes, 100.f*(n+1)/nnodes, timer.total()/1000.f);
      fflush(stdout);
    }

  }
  printf("\rMulti list: %s %zu/%zu (%.1f%%) elapsed=%.1f s\n",
      description, path.size(), nnodes, 100.f, timer.total()/1000.f);

  return path;
}

void sample_3edges(int &i, int &j, int &k, int nnodes) {
  do {
    i = rand() % (nnodes-1);
    j = rand() % (nnodes-1);
    k = rand() % (nnodes-1);
  } while (!(i != j) && (j != k) && (i != k));

  auto cas = [](int &a, int &b) {
    if (a > b) {
      int tmp = a;
      a = b;
      b = tmp;
    }
  };

  // 3-sorting network
  cas(i,k);
  cas(i,j);
  cas(j,k);
}

bool refine_4opt(Path& path, int time_limit) {
  int nnodes = path.size();
  int path_cost = path.cost();

  const int print_interval = 200.f; // [ms]
  const int print_skip = 100'000;
  auto print_timer_start = high_resolution_clock::now();
  auto global_timer_start = high_resolution_clock::now();

  int improvable;
  int uncrossed = 0;
  int delta;
  bool finished = true;

  printf("4-opt refinement: cost=%i uncrossed=0 elapsed=%.1f s",
      path_cost, 0.f);
  fflush(stdout);

  int skip_tracker = 0; // print skip tracker
  do {
    improvable = 0;
    for (int i = 1; i < nnodes-3; i++) {
      auto distance_pred_i = path.distance_idx(i-1, i);
      auto distance_i_succ = path.distance_idx(i, i+1);
      for (int j = i+1; j < nnodes-2; j++) {
        if (j == i+1) {
          delta =
            -distance_pred_i // -path.distance_idx(i-1, i)
            -distance_i_succ // -path.distance_idx(i, i+1)
            -path.distance_idx(j, j+1)
            +path.distance_idx(i-1, j)
            +path.distance_idx(j, i)
            +path.distance_idx(i, j+1);
        } else {
          delta =
            -distance_pred_i // -path.distance_idx(i-1, i)
            -distance_i_succ // -path.distance_idx(i, i+1)
            -path.distance_idx(j-1, j)
            -path.distance_idx(j, j+1)
            +path.distance_idx(i-1, j)
            +path.distance_idx(j, i+1)
            +path.distance_idx(j-1, i)
            +path.distance_idx(i, j+1);
        }
        if (delta < 0) {
          path.swap(i, j);
          path_cost += delta;
          if (path_cost != path.cost()) {
            cout << "ERROR\n";
          }
          improvable = 1;
          uncrossed++;
          distance_pred_i = path.distance_idx(i-1, i);
          distance_i_succ = path.distance_idx(i, i+1);
        }

        // handling prints
        if (skip_tracker++ % print_skip == 0) {
          auto now = high_resolution_clock::now();
          auto elapsed = duration_cast<milliseconds>(
              now - global_timer_start).count();
          auto interval = duration_cast<milliseconds>(
              now - print_timer_start).count();
          if (interval > print_interval) { 
            printf("\r4-opt refinement: cost=%i uncrossed=%i elapsed=%.1f s",
                   path_cost, uncrossed, elapsed/1000.f);
            fflush(stdout);
            print_timer_start = high_resolution_clock::now();
          }
          if (elapsed >= time_limit) {
            goto time_out;
          }
        }
      }
    }
  } while (improvable);
  goto end;
time_out:
  finished = false;
  printf("\n4-opt refinement: timed out");
end:
  printf("\n");
  return finished;
}

bool refine_3opt(Path& path, DataFrame& dataframe, int time_limit) {
  const int nnodes = path.size();
  int path_cost = path.cost();

  // conversion from direct to indirect path representation
  vector<int> succ(nnodes);
  for (size_t i = 0; i < nnodes-1; i++) {
    succ[path[i]] = path[i+1];
  }
  succ[path[nnodes-1]] = -1;

  const int print_interval = 200.f; // [ms]
  const int print_skip = 100'000;
  auto print_timer_start = high_resolution_clock::now();
  auto global_timer_start = high_resolution_clock::now();

  int improvable;
  int uncrossed = 0;
  int delta;
  bool finished = true;
  unsigned int skip_tracker = 0;

  printf("3-opt refinement: cost=%i uncrossed=0 elapsed=%.1f s",
      path_cost, 0.f);
  fflush(stdout);

	do
	{
		improvable = 0;
loop_from_scratch:
    int start = path[0];
		int node_a = start;
		int node_b = succ[node_a];
		while (succ[succ[node_b]] != -1) {
			int node_c = succ[node_b];
			int node_d = succ[node_c];
			while (succ[node_d] != -1) {
				int node_e = succ[node_d];
				int node_f = succ[node_e];

				while (node_f != -1) {
          delta = 
            -dataframe.distance(node_a, node_b)
            -dataframe.distance(node_c, node_d)
            -dataframe.distance(node_e, node_f)
            +dataframe.distance(node_a, node_d)
            +dataframe.distance(node_c, node_f)
            +dataframe.distance(node_e, node_b);
					if (delta < 0) {
						// crossing edges
						succ[node_a] = node_d;
						succ[node_e] = node_b;
						succ[node_c] = node_f;
            improvable = 1;
            path_cost += delta;
            uncrossed++;
					}
          if (skip_tracker++ % print_skip == 0) {
            auto now = high_resolution_clock::now();
            auto elapsed = duration_cast<milliseconds>(
                now - global_timer_start).count();
            auto interval = duration_cast<milliseconds>(
                now - print_timer_start).count();
            if (interval > print_interval) {
              printf("\r3-opt refinement: cost=%i uncrossed=%i elapsed=%.1f s",
                     path_cost, uncrossed, elapsed/1000.f);
              fflush(stdout);
              print_timer_start = high_resolution_clock::now();
            }
            if (elapsed >= time_limit) {
              goto time_out;
            }
          }
          if (delta < 0) {
						goto loop_from_scratch;
          }
					node_e = succ[node_e];
					node_f = succ[node_e];
				}
				node_c = succ[node_c];
				node_d = succ[node_c];
			}
			node_a = succ[node_a];
			node_b = succ[node_a];
		}
	} while (improvable);
time_out:
  finished = false;
  printf("\n3-opt refinement: timed out\n");
  // converting back to the direct representation
  for (size_t i = 1; i < nnodes; i++) {
    path[i] = succ[path[i-1]];
  }
  return finished;
}

bool refine_2opt(Path& path, int time_limit) {
  int nnodes = path.size();
  int initial_cost = path.cost();
  int path_cost = initial_cost;
  auto print_timer = LTimer(200); // [ms]
  auto limit_timer = LTimer(time_limit);

  int improvable;
  int uncrossed = 0;
  int delta;
  bool finished = true;

  auto update = [&]() {
    double improvement = 1.0 - ((double)path_cost / initial_cost);
    printf("\r2-opt refinement: cost=%i (%.2f%%) uncrossed=%i elapsed=%.1f s",
       path_cost, -improvement*100, uncrossed, limit_timer.total()/1000.f);
    fflush(stdout);
  };
  update();

  do {
    improvable = 0;
    for (int i = 0; i < nnodes-2; i++) {
      auto distance_i = path.distance_idx(i, i+1);
      for (int j = i+2; j < nnodes-1; j++) {
        delta =
          -distance_i //-path.distance_idx(i, i+1)
          -path.distance_idx(j, j+1)
          +path.distance_idx(i, j)
          +path.distance_idx(i+1, j+1);
        if (delta < 0) {
          path_cost += delta;
          for (int k = 0; k < (j-i) / 2; k++) {
            path.swap(i+k+1, j-k);
          }
          improvable = 1;
          uncrossed++;
          distance_i = path.distance_idx(i, i+1);

        }
      }
      if (print_timer.uplap()) {
        update();
      }
      if (limit_timer.up()) {
        update();
        printf("\n2-opt refinement: timed out");
        finished = false;
        goto end;
      }
    }
  } while (improvable);
end:
  printf("\n");
  return finished;
}

bool refine_2opt_exhaustive(Path& path, int time_limit) {
  const int nnodes = path.size();
  int initial_cost = path.cost();
  int path_cost = initial_cost;

  auto print_timer = LTimer(200); // [ms]
  auto limit_timer = LTimer(time_limit);

  int improvable;
  int uncrossed = 0;
  int delta, best_delta;
  int best_i, best_j;
  bool finished = true;

  auto update = [&]() {
    double improvement = 1.0 - ((double)path_cost / initial_cost);
    printf("\r2-opt refinement (e): cost=%i (%.2f%%) uncrossed=%i elapsed=%.1f s",
       path_cost, -improvement*100, uncrossed, limit_timer.total()/1000.f);
    fflush(stdout);
  };
  update();

  do {
    improvable = 0;
    best_delta = 0;
    for (int i = 0; i < nnodes-2; i++) {
      auto distance_i = path.distance_idx(i, i+1);
      for (int j = i+2; j < nnodes-1; j++) {
        delta =
          -distance_i //-path.distance_idx(i, i+1)
          -path.distance_idx(j, j+1)
          +path.distance_idx(i, j)
          +path.distance_idx(i+1, j+1);
        if (delta < best_delta) {
          best_delta = delta;
          best_i = i;
          best_j = j;
        }

      }
      if (print_timer.uplap()) {
        update();
      }
      if (limit_timer.up()) {
        update();
        printf("\n2-opt refinement (e): timed out");
        finished = false;
        goto end;
      }
    }
    if (best_delta < 0) {
      path_cost += best_delta;
      for (int k = 0; k < (best_j-best_i) / 2; k++) {
        path.swap(best_i+k+1, best_j-k);
      }
      improvable = 1;
      uncrossed++;
    }
  } while (improvable);
  goto end;
end:
  printf("\n");
  return finished;
}

void diversificate(Path& path, int nkicks=1) {
  printf("\rDiversification: kicks=%i ... ", nkicks);
  fflush(stdout);

  const auto nnodes = path.size();
  Path aux = path;

  Path *old_path = &path;
  Path *new_path = &aux;

  while (nkicks--) {
    int i, j, k, h;
    sample_3edges(i, j, k, nnodes);

    // replacing the 3 selected edges in the path
    // (i, i+1), (j, j+1), (k, k+1)
    (*new_path).clear();

    h = 0;
    while (h <= i) {
      (*new_path).add((*old_path)[h++]);
    }
    h = j+1;
    while (h <= k) {
      (*new_path).add((*old_path)[h++]);
    }
    h = i+1;
    while (h <= j) {
      (*new_path).add((*old_path)[h++]);
    }
    h = k+1;
    while (h < nnodes) {
      (*new_path).add((*old_path)[h++]);
    }

    auto *tmp = old_path;
    old_path = new_path;
    new_path = tmp;
  }
  if (nkicks % 2 == 1) {
    path = aux;
  }
  cout << "done\n";
}

void vns(Path& path, int time_limit) {
  int time_left, elapsed;
  int initial_cost, new_cost;

  auto timer_start = high_resolution_clock::now();

  printf("Variable Neighborhood Search (VNS)\n");
  printf("Time limit: %.1f s\n", time_limit/1000.f);

  initial_cost = new_cost = path.cost();
  cout << "Initial cost: " << initial_cost << "\n";

  elapsed = duration_cast<milliseconds>(
      high_resolution_clock::now() - timer_start).count();
  time_left = time_limit - elapsed;

  printf("Time left: %.1f s\n\n", time_left/1000.f);

  auto best_path = path;
  int best_cost = new_cost;

  int round;
  int nnodes = path.size();
  int min_kicks = max(1, nnodes/1'000);
  int nkicks = min_kicks;
  int trial = 0;

  for (round = 1; ; round++) {
    cout << "Round: " << round << endl;

    elapsed = duration_cast<milliseconds>(
        high_resolution_clock::now() - timer_start).count();
    time_left = time_limit - elapsed;
    refine_2opt(path, time_left);
    new_cost = path.cost();

    if (new_cost < best_cost) {
      best_cost = new_cost;
      best_path = path;
      cout << " *** Found new best solution! ";
      double improvement = 1.0 - ((double)best_cost / initial_cost);
      printf("Total improvement: %.2f%%\n", improvement*100);
      nkicks = min_kicks;
      trial = 0;
    } else {
      trial++;
    }

    elapsed = duration_cast<milliseconds>(
        high_resolution_clock::now() - timer_start).count();
    time_left = time_limit - elapsed;
    if (time_left <= 0) {
      break;
    }
    if (trial >= 5) {
      nkicks = 2 * min_kicks;
    }

    diversificate(path, nkicks);
    elapsed = duration_cast<milliseconds>(
        high_resolution_clock::now() - timer_start).count();
    time_left = time_limit - elapsed;
    printf("Time left: %.1f s\n", time_left/1000.f);
    cout << endl;
  }

  cout << endl;
  cout << "Final cost: " << best_cost << "\n";
  double improvement = 1.0 - ((double)best_cost / initial_cost);
  printf("Total improvement: %.2f%%\n", improvement*100);

  path = best_path;
}

