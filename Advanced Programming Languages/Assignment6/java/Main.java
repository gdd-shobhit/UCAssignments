import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Multi-threaded data processing system: producer adds ride tasks to a shared queue,
 * workers process them and write results to a shared list and output file.
 */
public class Main
{
    private static final Logger logger = Logger.getLogger(Main.class.getName());
    private static final int NumberOfWorkers = 4;
    private static final int NumberOfTasks = 12;
    private static final String OutputFile = "results.txt";

    public static void main(String[] arguments)
    {
        TaskQueue taskQueue = new TaskQueue();
        BlockingQueue<Task> queue = taskQueue.GetQueue();
        List<String> results = Collections.synchronizedList(new ArrayList<>());
        ReentrantLock resultsLock = new ReentrantLock();

        ExecutorService executor = Executors.newFixedThreadPool(NumberOfWorkers);

        try
        {
            for (int index = 0; index < NumberOfWorkers; index++)
            {
                executor.submit(new Worker(index + 1, queue, results, resultsLock));
            }

            AddTasks(taskQueue);
            SignalNoMoreTasks(taskQueue);

            executor.shutdown();
            if (!executor.awaitTermination(60, TimeUnit.SECONDS))
            {
                logger.warning("Executor did not terminate in time");
                executor.shutdownNow();
            }

            WriteResultsToFile(results, resultsLock);
            PrintSummary(results);
        }
        catch (InterruptedException exception)
        {
            logger.log(Level.SEVERE, "Main interrupted", exception);
            Thread.currentThread().interrupt();
            executor.shutdownNow();
        }
    }

    private static void AddTasks(TaskQueue taskQueue)
    {
        String[][] rides =
        {
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
            {"R012", "Downtown -> University"}
        };
        int count = Math.min(NumberOfTasks, rides.length);
        for (int index = 0; index < count; index++)
        {
            try
            {
                taskQueue.AddTask(new Task(rides[index][0], rides[index][1]));
            }
            catch (InterruptedException exception)
            {
                logger.log(Level.SEVERE, "Interrupted while adding task", exception);
                Thread.currentThread().interrupt();
                return;
            }
        }
        logger.info("Producer: added " + count + " tasks to queue");
    }

    private static void SignalNoMoreTasks(TaskQueue taskQueue)
    {
        try
        {
            for (int index = 0; index < NumberOfWorkers; index++)
            {
                taskQueue.AddShutdown();
            }
        }
        catch (InterruptedException exception)
        {
            logger.log(Level.SEVERE, "Interrupted while adding shutdown signals", exception);
            Thread.currentThread().interrupt();
        }
    }

    private static void WriteResultsToFile(List<String> results, ReentrantLock resultsLock)
    {
        Path path = Paths.get(OutputFile);
        try (BufferedWriter writer = Files.newBufferedWriter(path))
        {
            resultsLock.lock();
            try
            {
                for (String line : results)
                {
                    writer.write(line);
                    writer.newLine();
                }
            }
            finally
            {
                resultsLock.unlock();
            }
            logger.info("Wrote " + results.size() + " results to " + OutputFile);
        }
        catch (IOException exception)
        {
            logger.log(Level.SEVERE, "Failed to write results file: " + path, exception);
        }
    }

    private static void PrintSummary(List<String> results)
    {
        System.out.println("--- Summary: " + results.size() + " tasks processed ---");
        for (String result : results)
        {
            System.out.println(result);
        }
    }
}
