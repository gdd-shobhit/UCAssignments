package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"sync"
	"time"
)

const (
	numberOfWorkers   = 4
	numberOfTasks     = 12
	delayMilliseconds = 50
	outputFile        = "results.txt"
)

// Task represents a ride request to be processed.
type Task struct {
	Identifier string
	Payload    string
}

func main() {
	taskChannel := make(chan Task, numberOfTasks+numberOfWorkers)
	var resultsMutex sync.Mutex
	var results []string
	var waitGroup sync.WaitGroup

	// Start workers
	for index := 1; index <= numberOfWorkers; index++ {
		waitGroup.Add(1)
		go Worker(index, taskChannel, &results, &resultsMutex, &waitGroup)
	}

	// Producer: add tasks
	rides := [][2]string{
		{"R001", "Downtown -> Airport"},
		{"R002", "Mall -> Station"},
		{"R003", "Hotel -> Convention Center"},
		{"R004", "University -> Downtown"},
		{"R005", "A St -> B St"},
		{"R006", "C St -> D St"},
		{"R007", "Home -> Office"},
		{"R008", "Office -> Airport"},
		{"R009", "Station -> Mall"},
		{"R010", "Airport -> Downtown"},
		{"R011", "Convention Center -> Hotel"},
		{"R012", "Downtown -> University"},
	}
	count := numberOfTasks
	if count > len(rides) {
		count = len(rides)
	}
	for index := 0; index < count; index++ {
		taskChannel <- Task{Identifier: rides[index][0], Payload: rides[index][1]}
	}
	close(taskChannel)
	log.Printf("Producer: added %d tasks, closed task channel", count)

	waitGroup.Wait()

	if fileError := WriteResultsToFile(outputFile, &results, &resultsMutex); fileError != nil {
		log.Printf("Error writing results file: %v", fileError)
	}

	PrintSummary(&results, &resultsMutex)
}

func Worker(identifier int, taskChannel <-chan Task, results *[]string, resultsMutex *sync.Mutex, waitGroup *sync.WaitGroup) {
	defer waitGroup.Done()
	log.Printf("Worker %d started", identifier)

	defer func() {
		if recovered := recover(); recovered != nil {
			log.Printf("Worker %d panic recovered: %v", identifier, recovered)
		}
	}()

	for task := range taskChannel {
		time.Sleep(delayMilliseconds * time.Millisecond)
		result := fmt.Sprintf("Processed: %s -> %s (by worker %d)", task.Identifier, task.Payload, identifier)

		resultsMutex.Lock()
		*results = append(*results, result)
		resultsMutex.Unlock()

		log.Printf("Worker %d completed task %s", identifier, task.Identifier)
	}

	log.Printf("Worker %d completed", identifier)
}

func WriteResultsToFile(fileName string, results *[]string, resultsMutex *sync.Mutex) error {
	file, fileError := os.Create(fileName)
	if fileError != nil {
		return fileError
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	resultsMutex.Lock()
	for _, line := range *results {
		if _, writeError := writer.WriteString(line + "\n"); writeError != nil {
			resultsMutex.Unlock()
			return writeError
		}
	}
	resultsMutex.Unlock()

	if flushError := writer.Flush(); flushError != nil {
		return flushError
	}
	log.Printf("Wrote %d results to %s", len(*results), fileName)
	return nil
}

func PrintSummary(results *[]string, resultsMutex *sync.Mutex) {
	resultsMutex.Lock()
	defer resultsMutex.Unlock()
	fmt.Printf("--- Summary: %d tasks processed ---\n", len(*results))
	for _, result := range *results {
		fmt.Println(result)
	}
}
