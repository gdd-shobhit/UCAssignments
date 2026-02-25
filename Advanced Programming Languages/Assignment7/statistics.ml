let mean lst =
  if lst = [] then 0.0
  else
    let sum = List.fold_left ( + ) 0 lst in
    float_of_int sum /. float_of_int (List.length lst)

let median lst =
  if lst = [] then 0.0
  else
    let sorted = List.sort compare lst in
    let n = List.length sorted in
    let mid = n / 2 in
    if n mod 2 = 1 then float_of_int (List.nth sorted mid)
    else
      let a = List.nth sorted (mid - 1) in
      let b = List.nth sorted mid in
      (float_of_int a +. float_of_int b) /. 2.0

let frequency_list lst =
  let add m x =
    let c = try List.assoc x m with Not_found -> 0 in
    (x, c + 1) :: List.remove_assoc x m
  in
  List.fold_left add [] lst

let mode lst =
  if lst = [] then []
  else
    let counts = frequency_list lst in
    let max_count = List.fold_left (fun m (_, c) -> max m c) 0 counts in
    List.map fst (List.filter (fun (_, c) -> c = max_count) counts)
    |> List.sort_uniq compare

let () =
  let data = [ 4; 2; 3; 2; 5; 2; 4 ] in
  Printf.printf "Data: %s\n" (String.concat " " (List.map string_of_int data));
  Printf.printf "Mean: %.2f\n" (mean data);
  Printf.printf "Median: %.2f\n" (median data);
  Printf.printf "Mode: %s\n" (String.concat " " (List.map string_of_int (mode data)))
