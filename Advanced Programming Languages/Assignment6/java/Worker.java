import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Worker that takes tasks from the shared queue, processes them (simulated delay),
 * and appends results to the shared list.
 */
public class Worker implements Runnable
{
    private static final Logger logger = Logger.getLogger(Worker.class.getName());
    private static final int ProcessDelayMilliseconds = 50;

    private final int workerIdentifier;
    private final BlockingQueue<Task> queue;
    private final List<String> results;
    private final ReentrantLock resultsLock;

    public Worker(int workerIdentifier, BlockingQueue<Task> queue, List<String> results, ReentrantLock resultsLock)
    {
        this.workerIdentifier = workerIdentifier;
        this.queue = queue;
        this.results = results;
        this.resultsLock = resultsLock;
    }

    @Override
    public void run()
    {
        String threadName = Thread.currentThread().getName();
        logger.info(String.format("[%s] Worker %d started", threadName, workerIdentifier));

        try
        {
            while (true)
            {
                Task task = queue.take();

                if (Task.IsShutdown(task))
                {
                    logger.info(String.format("[%s] Worker %d received shutdown signal, exiting", threadName, workerIdentifier));
                    break;
                }

                try
                {
                    ProcessTask(task, threadName);
                }
                catch (Exception exception)
                {
                    logger.log(Level.SEVERE, String.format("[%s] Worker %d error processing task %s", threadName, workerIdentifier, task.GetIdentifier()), exception);
                }
            }
        }
        catch (InterruptedException exception)
        {
            logger.log(Level.WARNING, String.format("[%s] Worker %d interrupted", threadName, workerIdentifier), exception);
            Thread.currentThread().interrupt();
        }

        logger.info(String.format("[%s] Worker %d completed", threadName, workerIdentifier));
    }

    private void ProcessTask(Task task, String threadName) throws InterruptedException
    {
        Thread.sleep(ProcessDelayMilliseconds);
        String result = String.format("Processed: %s -> %s (by worker %d)", task.GetIdentifier(), task.GetPayload(), workerIdentifier);

        resultsLock.lock();
        try
        {
            results.add(result);
        }
        finally
        {
            resultsLock.unlock();
        }

        logger.info(String.format("[%s] Worker %d completed task %s", threadName, workerIdentifier, task.GetIdentifier()));
    }
}
