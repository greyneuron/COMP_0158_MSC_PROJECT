#include <iostream>
#include <fstream>
#include <string>
#include <regex>

#include <ctime>
#include <iomanip>
#include <sstream>


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
    
    std::string disorder_file = "extras_part_test.xml";
    //std::string output_file = "extras_mobidb_only.xml";

    std::string timestamp = getCurrentTimestamp();

    std::string output_file = "extras_mobidb_" + timestamp + "_.xml";

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

    bool match = false;
    int protein_count = 0;
    //int protein_limit = 1100;
    int line_number = 0;

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

            if(protein_count >= protein_limit){
                //std::cout<< "limit reached at line " << line_number << line << std::endl;
                //of << "---------------" << std::endl;
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
    file.close();
    of.close();

    //std::cout << std::endl << "Buffer contents:\n" << buffer << std::endl;
    //std::cout << "found " << protein_count << " from " <<  start_line << " to " << line_number << std::endl;

    return line_number;
}

int main() {
    int start_line = 0;
    int proteins_limit = 2;
    
    int line_number = parse_file(proteins_limit, start_line);
    std::cout << "Found to line " << line_number << std::endl;

    line_number = parse_file(proteins_limit, line_number);
    std::cout << "Found to line " << line_number;
}
