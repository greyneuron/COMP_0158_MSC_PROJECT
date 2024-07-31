#include <iostream>
#include <fstream>
#include <string>
#include <regex>

#include <ctime>
#include <iomanip>
#include <sstream>

#include <chrono>

using std::chrono::high_resolution_clock;
using std::chrono::duration_cast;
using std::chrono::milliseconds;

// To compile you need to link the pugixml lib
// g++ split_files.cpp -o split_files
// g++ -std=c++11 split_files.cpp -o split_files
// sudo split_files

std::string getCurrentTimestamp() {
    // Get the current time
    std::time_t now = std::time(nullptr);
    std::tm* localTime = std::localtime(&now);

    // Create a string stream to format the time
    std::ostringstream oss;
    oss << std::put_time(localTime, "%Y%m%d_%H%M");

    // Return the formatted string
    return oss.str();
}


int parse_file(int protein_limit, int start_line){
    // Define the path to the file
    // std::string disorder_file = "/Volumes/My Passport 3/downloads/extra.xml";
    //std::string output_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/disorder/disorder.dat";
    
    //std::string disorder_file = "extras_part_test.xml";
    //std::string disorder_file = "/Volumes/My Passport 3/downloads/extra.xml";
    std::string disorder_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/extras_part_20.xml";

    std::string timestamp = getCurrentTimestamp();
    std::string output_file = "extras_mobidb_" + timestamp + "_.xml";

    auto start = high_resolution_clock::now();

    // Open the file
    std::ifstream file(disorder_file);
    std::ofstream of(output_file, std::ios::app); // open file to append
    
    // Check if the file was successfully opened
    if (!file.is_open()) {
        std::cerr << "Could not open the file!" << std::endl;
        return 1;
    }

    std::string buffer;
    std::string line;
    
    std::regex start_pattern("<protein");
    std::regex end_pattern("protein>");
    std::smatch matches;

    bool match          = false;
    bool limit_reached  = false;
    int protein_count   = 0;
    int line_number     = 0;

    // read each line
    while (std::getline(file, line)) {
        line_number += 1;

        if ( (start_line > 0) && (line_number <= start_line) ){
            //std::cout << line_number << ": not ready to parse" << line << std::endl;
            continue;
        }
        // Check if the line contains the keyword
        if(std::regex_search(line, matches, end_pattern)){
            //std::cout << "Found protein end line " << line << std::endl;
            buffer += line + "\n";
            protein_count +=1;
            match = false;

            // if have reached the max number of proteins to put in a file
            // then ouput the buffer to the file and break from the loop
            if(protein_count >= protein_limit){
                //std::cout<< "limit reached at line " << line_number << line << std::endl;
                //of << "---------------" << std::endl;
                limit_reached = true;
                of << buffer;
                break;
            }
        }
        else if(match){
            //std::cout << "Match is true. current line " << line << std::endl;
            buffer += line + "\n";
        }
        else if(std::regex_search(line, matches, start_pattern)){
            //std::cout << "Found protein start line " << line << std::endl;
            buffer += line + "\n";
            match = true;
        }
        else{
            //std::cout << "Match is false, ignoring line" << line << std::endl;
        }
    }
    // check if there's anything left to ouput
    if (! limit_reached){
        
        of << buffer;
        file.close();
        of.close();
        auto end = high_resolution_clock::now();
        auto duration = duration_cast<milliseconds>(end - start);
        std::cout<< "Reached end of file. Protein count: " << protein_count << " time: " << duration.count() << " output: " << output_file << std::endl;
        return -1;
    }else{
        file.close();
        of.close();
        auto end = high_resolution_clock::now();
        auto duration = duration_cast<milliseconds>(end - start);
        std::cout<< "Reached protein limit. Protein count: " << protein_count << " time: " <<  duration.count() << std::endl;
        return line_number;
    }
}

int main() {
    int proteins_limit  = 100000; // proteins in each buffer
    int next_start      = 0;
    
    // run first pass
    //next_start = parse_file(proteins_limit, 0);

    while(next_start != -1){
        next_start = parse_file(proteins_limit, next_start);
        //std::cout << "Found to line " << next_start << std::endl;
    }
}
