public class Assignment2Section2Java 
{
    public static void main(String[] args) 
    {
        int[] numbers = new int[5]; // heap allocation

        for (int i = 0; i < numbers.length; i++) 
            {
            numbers[i] = i + 1;
        }

        printSum(numbers);

        // Optional: I like to assign things to null after usage to free memory
        // Even if it wasnt null, it would have been collected after the scope ends
        // But if there was more stuff after the print, it would have not been freed
        numbers = null;
    } // GC collects numbers are it goes out of scope here

    static void printSum(int[] data) 
    {
        int sum = 0;
        for (int n : data) 
        {
            sum += n;
        }
        System.out.println("Sum: " + sum);
    }
}
