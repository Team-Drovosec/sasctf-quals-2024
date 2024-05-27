#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <cassert>
#include <algorithm>
#include <random>

const int TAPE_SIZE=24;
using namespace std;

template<typename T>
ostream& operator<<(ostream& out, vector<T> v) {
    for(int i = 0; i<v.size(); i++) {
        out << v[i] << "  ";
    }
    return out;
}

char inttohex(int a) {
    if(0 <= a && a <= 9) {
        return a + '0';
    } else {
        return a - 10 + 'a';
    }
}

string calc (int inp) {
    // cout << inp << endl;
    vector<bool> tape;
    // fill tape
    for(char c : std::bitset<TAPE_SIZE>(inp).to_string()) {
        tape.push_back(c == '1');
    }
    vector<int> opseq = {1, 2, 1, 0, 1, 3, 0, 1, 2, 3, 0, 1, 0, 3, 2, 3, 3, 3, 3, 3};
    for (int opi = 0; opi<opseq.size(); opi++) {
        // cout << "=====" << endl;
        // cout << opseq[opi] << endl;
        // cout << opseq << endl;
        // cout << tape << endl;
        if (opi > 100) {
            return "STUCK";
        }
        int op = opseq[opi];
        // cout << op << endl;
        if(op == 0) { // swap with gap 2
            for(int i = 0; i + 3 < TAPE_SIZE; i++) {
                bool a = tape[i];
                bool b = tape[i + 3];
                tape[i] = b;
                tape[i + 3] = a;
            }
        } else if (op == 1) { // swap with gap 1
            for(int i = 0; i + 2 < TAPE_SIZE; i++) {
                bool a = tape[i];
                bool b = tape[i + 2];
                tape[i] = b;
                tape[i + 2] = a;
            }
        } else if (op == 2) { // swap adjacent
            for(int i = 0; i + 1 < TAPE_SIZE; i++) {
                bool a = tape[i];
                bool b = tape[i + 1];
                tape[i] = b;
                tape[i + 1] = a;
            }
        } else if (op == 3) { // count "10", add such ops, first not being 4
            int sum = 0;
            for(int i = 0; i + 1 < TAPE_SIZE; i++) {
                if (tape[i] == 1 && tape[i + 1] == 0) {
                    sum++;
                }
            }
            int op1 = sum & 0b11;
            int op2 = (sum & 0b1100) >> 2;
            // cout << op1 << " " << op2 << endl;
            opseq.push_back(op1);
            opseq.push_back(op2);
        }
    }
    // cout << "FINAL TAPE" << endl;
    // cout << tape << endl;
    string res = "";
    for(int i = 0; i<TAPE_SIZE; i+=4) {
        char a = tape[i];
        char b = tape[i+1] * 2;
        char c = tape[i+2] * 4;
        char d = tape[i+3] * 8;
        res += inttohex(a + b + c + d);
    }
    // cout << res << endl;
    return res;
}

int main() {
    // string res = calc(939113);
    // cout << res << endl;
    map<string, int> counts;
    map<string, int> last;
    for(int i = 0; i<(1<<TAPE_SIZE); i++) {
        if(i % 100000 == 0) {
            cout << i << endl;
        }
        // for(int j = 0; j < TAPE_SIZE; j++) {
        //     if ((i >> j) & 1) {
        //         cout << 1;
        //     } else {
        //         cout << 0;
        //     }
        // }
        // cout << " -> ";
        string res = calc(i);
        // cout << res << endl;
        if(res == "487fe5") {
            cout << std::bitset<TAPE_SIZE>(i).to_string() << endl;
            return 0;
        }
        // counts[res]++;
        // last[res] = i;
    }
    vector<pair<int, string>> unique;
    for (auto const& [res, occur] : counts)
    {
        // std::cout << key << ':' << val << std::endl;
        if(occur == 1) {
            int inp = last[res];
            string inps = std::bitset<TAPE_SIZE>(inp).to_string();
            if(count(inps.begin(), inps.end(), '0') == 10) {
                unique.emplace_back(inp, res);
                cout << inp << ": " << inps << " -> " << res << endl;
                assert(calc(inp) == res);
            }
        } else if (occur == 0) {
            cout << "No input for " + res << endl;
        }
    }
    cout << "possibilities: " << counts.size() << endl;
    cout << "unique: " << unique.size() << endl; 
    mt19937 g(42);
 
    shuffle(unique.begin(), unique.end(), g);
    cout << unique[0].first << " " << unique[0].second << endl;
    assert(calc(unique[0].first) == unique[0].second);
    int selinp = unique[0].first;
    string selinps = std::bitset<TAPE_SIZE>(selinp).to_string();
    cout << selinps << " -> " << calc(selinp) << endl;
}