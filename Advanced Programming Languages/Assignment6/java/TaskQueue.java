import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

/**
 * Shared queue with AddTask() and GetTask() and synchronized access.
 */
public class TaskQueue
{
    private final BlockingQueue<Task> queue = new LinkedBlockingQueue<>();

    public void AddTask(Task task) throws InterruptedException
    {
        queue.put(task);
    }

    /**
     * Blocking get: returns next task or shutdown sentinel. Does not return null.
     */
    public Task GetTask() throws InterruptedException
    {
        return queue.take();
    }

    public void AddShutdown() throws InterruptedException
    {
        queue.put(Task.Shutdown());
    }

    public BlockingQueue<Task> GetQueue()
    {
        return queue;
    }
}
