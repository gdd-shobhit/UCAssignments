fn main()
{
    let numbers = vec![1, 2, 3, 4, 5]; // heap allocation

    print_sum(&numbers); // borrowed immutably
}

fn print_sum(data: &Vec<i32>)
{
    let sum: i32 = data.iter().sum();
    println!("Sum: {}", sum);
    // If ownership was taken, data would be dropped here. But since it's borrowed, it remains valid.
}
